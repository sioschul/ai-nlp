import copy
import operator
from collections import Counter

import gensim
import itertools

import nltk
from sklearn.feature_extraction.text import CountVectorizer
import functions as fn

# match entities first certain matching then fuzzy matching
def non_fuzzy_entity_matching(single_word_ents, multi_word_ents, languaga):
    # single word ents matched against multi word entities
    matched_ents = match_single_against_multi_word(single_word_ents, multi_word_ents)
    # ambiguous multi word entities
    ambiguous = find_ambiguous_words(matched_ents)
    # unambiguous matches and first name matches ('Harry', 'Harry_Potter')
    matched, amb = direct_matching(matched_ents, ambiguous, languaga)
    return matched, amb


# sorts the sentences with ambiguous mentions via majority vote
def fuzzy_entity_matching(amb, matched, sentences, entity_frequency, common_sentences, cooc, single_ents, multi_ents,
                          accuracy_gensim, accuracy_frequency, accuracy_lookaround):
    # create coocurence matrix and gensim model
    modelo, X = create_cooccurence(cooc)
    modelg = create_gensim(sentences)
    fuzzy_sentences = copy.deepcopy(common_sentences)
    for ind, x in amb.items():
        # these votes don't change for different mentions because the consider all sentences not just the current
        gensim_num = gensim_matching(ind, x, modelg, accuracy_gensim)
        overall = overall_frequency_matching(x, matched, entity_frequency, accuracy_frequency)
        # compute results for all fuzzy matching methods for each ambiguous mention of ind
        for i, s in common_sentences[ind].items():
            decisions = [gensim_num, overall, co_occurence_matching(ind, x, modelo, X, s, single_ents, multi_ents, matched)]
            # frequency before and after current mention
            before, after = lookaround_frequency_matching(x, sentences, s, accuracy_lookaround)
            decisions.append(before)
            decisions.append(after)
            # remove empty votes
            decisions = list(filter(lambda a: a != '', decisions))
            vote = ''
            vote_count = Counter(decisions)
            # get majority vote
            if vote_count != Counter():
                vote = max(vote_count.items(), key=operator.itemgetter(1))[0]
            # shift sentence according to vote
            # do nothing if not decideable
            if vote != ''and vote_count[vote] != 1 or len(decisions) ==1:
                fuzzy_sentences[vote][i] = s
                del fuzzy_sentences[ind][i]
    return fuzzy_sentences



# matching all single word entities against fitting multi word entities
def match_single_against_multi_word(single_word_ents, multi_word_ents):
    # match single words against multi words
    matched_ents = {}
    for i in single_word_ents:
        belong_together = []
        for j in multi_word_ents:
            if i in j:
                belong_together.append(j)
        if i not in matched_ents.keys():
            matched_ents[i] = belong_together
    # add remaining multi word entities to matched_ents which do not have a single word counterpart
    multi_to_add = []
    for i in multi_word_ents:
        found = False
        for sublist in matched_ents.values():
            if i in sublist:
                found = True
                break
        if not found:
            multi_to_add.append(i)
    for i in multi_to_add:
        matched_ents[i] = []
    return matched_ents


# returns a list of entities that are ambiguous
def find_ambiguous_words(matched_ents):
    amb = []
    for ind, m in matched_ents.items():
        # if multiple multi words fit to a single word they are ambiguous
        if len(m) > 1:
            amb.extend(m)
        # if they are matched with more than one word they are ambiguous
        for ind2, m2 in matched_ents.items():
            for i in m:
                for j in m2:
                    if i == j and not ind == ind2 and j not in amb:
                        amb.append(j)
    return amb


# matching non ambiguous + first names:
def direct_matching(matched_ents, ambigous, language):
    honorifics = fn.load_honorifics(language)
    amb = {}
    # match all entities which are not ambiguous
    matched = []
    for ind, m in matched_ents.items():
        belong_together = [ind]
        for entry in m:
            if entry not in ambigous:
                belong_together.append(entry)
            # match ambiguous ones when they are first name matches
            else:
                if entry.startswith(ind + '_'):
                    belong_together.append(entry)
                else:
                    amb.setdefault(ind, []).append(entry)
        # if there are 2 possible matches for a last name and one is first name + last name and one a honorific + last name
        # most likely these mentions are the same person
        if len(m) == 2:
            if (m[0].endswith('_' + ind) and m[1].split('_')[0] in honorifics) or (
                    m[1].endswith('_' + ind) and m[0].split('_')[0] in honorifics):
                belong_together.append(m[0])
                belong_together.append(m[1])
                del amb[ind]
        matched.append(belong_together)
    # now unambiguous entities matched if there is a hind they belong together (start or end in common)
    delete = []
    for ind, m in amb.items():
        if len(m) == 1 and (m[0].startswith(ind) or m[0].endswith(ind) or ind.startswith(m[0]) or ind.endswith(m[0])):
            matched.append([ind, m[0]])
            for sl in matched:
                if sl == [ind]:
                    matched.remove(sl)
            delete.append(ind)
    for ind in delete:
        del amb[ind]
    # add remaining ambiguous entities as distinct entities
    for ind, m in matched_ents.items():
        for entry in m:
            found = False
            for sublist in matched:
                if entry in sublist:
                    found = True
                    break
            if not found:
                matched.append([entry])
    # transitivity [Harry,Harry_Potter] and [Harry_Potter,Mr_Potter] become [Harry, Harry_Potter, Mr_Potter]
    for sl in matched:
        for sl2 in matched:
            if sl != sl2 and not set(sl).isdisjoint(sl2):
                sl.extend(sl2)
    # remove duplicate lists
    for idx, sublist in enumerate(matched):
        temp = list(dict.fromkeys(sublist))
        temp.sort()
        matched[idx] = temp
    matched.sort()
    matched1 = list(matched for matched, _ in itertools.groupby(matched))
    return matched1, amb

def create_gensim(sentences):
    # gensim word embedding model
    data = []
    for i in sentences:
        i = i.replace('-', ' ')
        temp = []

        # tokenize the sentence into words
        for j in nltk.word_tokenize(i):
            temp.append(j)

        data.append(temp)
    model = gensim.models.Word2Vec(data, min_count=fn.min_occ, iter=10,
                                    size=100, window=5, sg=1)
    return model

def gensim_matching(ind, x, model, accuracy):
    # match ambiguos entites with most similar ones
    match = ''
    matches = {}
    # compute similarity score for possible matches
    for m in x:
        if m in model.wv.vocab and ind in model.wv.vocab:
            if model.wv.similarity(m, ind) > accuracy:
                matches[m] = model.wv.similarity(m, ind)
    # find and return highest rated match
    if len(matches) > 0:
        match = max(matches.items(), key=operator.itemgetter(1))[0]
    return match

# count over all frequency of possible matches and decide for the most common one
def overall_frequency_matching(x, matched, entity_frequency, accuracy):
    freq = accuracy
    matches ={}
    match = ''
    for m in x:
        # frequency of m is frequency of m + frequency of matches before
        freq_m = 0
        for sl in matched:
            if m in sl:
                for j in sl:
                    freq_m += entity_frequency[j]
        if freq_m > freq:
           matches[m] = freq_m
    if len(set(matches.values())) == len(matches.values()):
        match = max(matches.items(), key=operator.itemgetter(1))[0]
    return match

# check for occurrences of the possible matches around the current sentence and decide for the one which occurs the most
def lookaround_frequency_matching(x, sentences, current_sentence, accuracy):
    for ind1, se in enumerate(sentences):
        if current_sentence == se:
            count_mentions_before = []
            count_mentions_after = []
            # find sentences before and after
            for i in range(accuracy):
                if ind1 + i + 1 < len(sentences):
                    s1 = sentences[ind1 + i + 1]
                else:
                    s1 = ''
                if ind1 - i - 1 > 0:
                    s2 = sentences[ind1 - i - 1]
                else:
                    s2 = ''
                # check if m (possible match we look at) occurs in the selected sentences
                for m in x:
                    for word in s1.split(' '):
                        if word == m:
                            count_mentions_after.append(m)
                    for word in s2.split(' '):
                        if word == m:
                            count_mentions_before.append(m)
            match_b = ''
            match_a = ''
            count_b = Counter(count_mentions_before)
            count_a = Counter(count_mentions_after)
            # take the match with the highest frequency
            if count_a != Counter() and len(set(count_a.values())) == len(count_a.values()):
                match_a = max(count_a.items(), key=operator.itemgetter(1))[0]
            if count_b != Counter() and len(set(count_b.values())) == len(count_b.values()):
                match_b = max(count_b.items(), key=operator.itemgetter(1))[0]
            return match_b, match_a

# create cooccurrence matrix
def create_cooccurence(entities):
    count_model = CountVectorizer(ngram_range=(1, 1))  # default unigram model
    X = count_model.fit_transform(entities)
    return count_model, X

def co_occurence_matching(ind, x, model, X, sentence, single_ents, multi_ents,matched):
    Xc = (X.T * X)  # this is co-occurrence matrix in sparse csr format
    Xc.setdiag(0)  # fill same word concurrence to 0
    names = model.get_feature_names()
    matrix = Xc.todense()
    matches = {}
    match = ''
    for m in x:
        matches[m] = 0
    # find entity in matrix, check for all possible matches how often they cooccured
    for word in sentence.split(' '):
        if (word in single_ents or word in multi_ents) and word != ind and word not in x:
            word_ind = 0
            for i, w in enumerate(names):
                if w == word.lower():
                    word_ind = i
            for m in x:
                if m.lower() in names:
                    cooc_m = 0
                    for sl in matched:
                        if m in sl:
                            for j in sl:
                                j_ind = 0
                                for i, w in enumerate(names):
                                    if w == j.lower():
                                        j_ind = i
                                cooc_m += matrix[j_ind, word_ind]
                    matches[m] += cooc_m
    # choose the one with the highest amount of cooccurence
    if len(set(matches.values())) == len(matches.values()):
        match = max(matches.items(), key=operator.itemgetter(1))[0]
    return match

def sort_sentences_to_matched_entities(common_sentences, matched):
    # put sentences together based on matched entities
    # keys will be a tuple containing names that belong to the same entity
    # values will be all sentences where these names were tagged as entities
    sentences_matched = {}
    for sublist in matched:
        keys = ()
        item = sublist[0]
        for item2 in sublist:
            if item != item2:
                common_sentences[item].update(common_sentences[item2])
            if item2 not in keys:
                keys = keys + (item2,)
        sentences_matched[keys] = common_sentences[item]
    return sentences_matched

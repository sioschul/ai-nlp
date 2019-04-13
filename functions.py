import itertools

import gensim
import re

import nltk
import spacy
from collections import Counter

entity_frequency = Counter()

# read and tokenize book
def read_and_tokenize(book, current_sentence):
    # read book
    text = ''
    with open(book) as f:
        # read text until current sentence
        for line in f:
            if current_sentence in line.strip():
                break
            text = text + line
        # adding last line with current sentence
        text = text + line
    # split book into sentences
    sentences = nltk.tokenize.sent_tokenize(text)
    return sentences


# for stop word filtering
def load_stop_words(language):
    if language == 'en':
        spacy.load('en_core_web_sm')
        spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
        spacy_stopwords.add('yes')
        spacy_stopwords.add('no')
        spacy_stopwords.add('yeah')
        spacy_stopwords.add('hey')
    if language == 'de':
        spacy.load('de_core_news_sm')
        spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
        spacy_stopwords.add('ja')
        spacy_stopwords.add('nein')
        spacy_stopwords.add('yeah')
        spacy_stopwords.add('hey')
    if language == 'es':
        spacy.load('es_core_news_sm')
        spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
        spacy_stopwords.add('sí')
        spacy_stopwords.add('no')
        spacy_stopwords.add('yeah')
        spacy_stopwords.add('hey')
    if language == 'fr':
        spacy.load('fr_core_news_sm')
        spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
        spacy_stopwords.add('oui')
        spacy_stopwords.add('non')
        spacy_stopwords.add('yeah')
        spacy_stopwords.add('hey')
    if language == 'pt':
        spacy.load('pt_core_news_sm')
        spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
        spacy_stopwords.add('sim')
        spacy_stopwords.add('não')
        spacy_stopwords.add('yeah')
        spacy_stopwords.add('hey')
    if language == 'it':
        spacy.load('it_core_news_sm')
        spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
        spacy_stopwords.add('sì')
        spacy_stopwords.add('no')
        spacy_stopwords.add('yeah')
        spacy_stopwords.add('hey')
    return spacy_stopwords


# extracting entities and related sentences
def entity_extraction(sentences, language, min_occurence=6):
    global entity_frequency
    tokens = []
    sentences_by_ents = {}
    # load stopwords
    spacy_stopwords = load_stop_words(language)
    # load model
    nlp = spacy.load('xx_ent_wiki_sm')
    # spacy entity model
    for i, s in enumerate(sentences):
        s = re.sub('\s+', ' ', s)
        s = s.strip()
        doc = nlp(s)
        for ent in doc.ents:
            name = ent.text
            # replace whitespace in multi word ents with "_"
            if len(ent.text.split()) > 1:
                name = ent.text.replace(" ", "_")
                sentences[i] = sentences[i].replace(ent.text, name)
            if name.endswith("!") or name.endswith("?") or name.endswith("\'") or name.endswith("."):
                name = re.sub('[\.\'\!\?]$', '', name)
            # remove whitespaces from ents and remove stopwords from ents
            if name.lower() not in spacy_stopwords and not name.startswith('\'') and not name.startswith('\"') and name != '':
                # keep all sentences from the same entity together
                # assuming entities with the same name are always the same type/person in the same book
                sentences_by_ents.setdefault(name, []).append(sentences[i].strip())
                # keep track of entities with their tag
                tokens.append(name)

    # remove unnecessary entries with <6 occurrences4
    c = Counter(tokens)
    entity_frequency = c
    most_common = {k: c[k] for k in c if c[k] > min_occurence}
    common_sentences = {k: sentences_by_ents[k] for k in sentences_by_ents if len(sentences_by_ents[k]) > min_occurence}
    # reduce to list of names
    single_tokens = []
    for k in most_common.keys():
        if k not in single_tokens:
            single_tokens.append(k)
    return single_tokens, common_sentences


def divide_into_single_and_multi_word(single_tokens):
    # divide into single and multi word
    single_word_ents = []
    multi_word_ents = []
    for i in single_tokens:
        if "_" in i:
            multi_word_ents.append(i)
        else:
            single_word_ents.append(i)
    return single_word_ents, multi_word_ents


# match entities first certain matching then fuzzy matching
def entity_matching(sentences, single_word_ents, multi_word_ents, accuracy, rule):
    # single word ents matched against multi word ents
    matched_ents = match_single_against_multi_word(single_word_ents, multi_word_ents)
    # ambiguos multi word ents
    ambigous = find_ambiguos_words(matched_ents)
    # unambiguos matches and first name matches for ambiguos ones
    matched = direct_matching(matched_ents, ambigous)
    if rule == 1:
        # fuzzy matching with gensim
        matched_fuzzy = fuzzy_matching_gensim(sentences, single_word_ents, multi_word_ents, matched, accuracy)
    if rule == 2:
        # matching ambiguos entities based on entity frequency
        matched_fuzzy = frequency_matching(matched_ents, matched, accuracy)
    else:
        return matched
    return matched_fuzzy


# matching all single word ents against fitting multi word ents and add multi word ents with no matching single word
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
    # add remaining multi words
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

# returns a list of enitites that are ambiguos
def find_ambiguos_words(matched_ents):
    amb = []
    for ind, m in matched_ents.items():
        # if multiple multi words fit to a single word they are ambiguos
        if len(m) > 1:
            amb.extend(m)
        # if they are matched with more than one word they are ambiguos
        for ind2, m2 in matched_ents.items():
            for i in m:
                for j in m2:
                    if i == j and not ind == ind2 and j not in amb:
                        amb.append(j)
    return amb


# matching non ambiguos + first names:
def direct_matching(matched_ents, ambigous):
    # match all entities which are not ambiguos
    matched = []
    for ind, m in matched_ents.items():
        belong_together = [ind]
        for entry in m:
            if entry not in ambigous:
                belong_together.append(entry)
            # match ambiguos ones when they are first name matches
            else:
                if entry.startswith(ind + '_'):
                    belong_together.append(entry)
        matched.append(belong_together)
    # add remaining ambiguos entites as distinct entities
    for ind, m in matched_ents.items():
        for entry in m:
            found = False
            for sublist in matched:
                if entry in sublist:
                    found = True
                    break
            if not found:
                matched.append([entry])
    return matched


# fuzzy matching with gensim
def fuzzy_matching_gensim(sentences, single_word, multi_word, matched, accuracy):
    # gensim word embedding model
    data = []
    for i in sentences:
        temp = []

        # tokenize the sentence into words
        for j in nltk.word_tokenize(i):
            temp.append(j)

        data.append(temp)

    model1 = gensim.models.Word2Vec(data, min_count=2, iter=8,
                                    size=100, window=5, sg=1)
    # match each entity with the most similar other entitis
    for sl in matched:
        add = []
        for x in sl:
            for m in model1.wv.most_similar(x):
                if (m[0] in single_word or m[0] in multi_word) and m[0] not in sl:
                    if m[1] > accuracy:
                        add.append(m[0])
        sl.extend(add)
    # remove duplicate lists
    for sl in matched:
        sl.sort()
    matched.sort()
    matched = list(matched for matched, _ in itertools.groupby(matched))
    return matched

# match single words that are matched to multiple multi word entities to the most frequent one
def frequency_matching(matched_ents, matched, accuracy):
    global entity_frequency
    for ind, m in matched_ents.items():
        # has been matched before = skip
        if len(m) > 1:
            first_name_matched = False
            for x in m:
                if x.startswith(ind + '_'):
                    first_name_matched = True
            # has not been matched vet
            if not first_name_matched:
                freq = accuracy
                match = ''
                for x in m:
                    if entity_frequency[x] > freq:
                        freq = entity_frequency[x]
                        match = x
                # append the most frequent match and remove its mention as distinct match
                if match != '':
                    for sl in matched:
                        if ind in sl:
                            sl.append(match)
                        if sl == [match]:
                            matched.remove(sl)
    # transitivity: we have not [Harry, Harry Potter] and [Potter, Harry Potter] we want [Harry, Harry Potter, Potter]
    for sl in matched:
        for sl2 in matched:
            if sl != sl2 and len(set(sl).intersection(sl2)) > 0:
                sl.extend(sl2)
    # remove duplicate lists
    for idx, sublist in enumerate(matched):
        temp = list(dict.fromkeys(sublist))
        temp.sort()
        matched[idx] = temp
    matched.sort()
    matched = list(matched for matched, _ in itertools.groupby(matched))
    return matched



def sort_sentences_to_matched_entities(common_sentences, matched):
    # put sentences together based on matched entities
    sentences_matched = {}
    for sublist in matched:
        keys = ()
        item = sublist[0]
        for item2 in sublist:
            if item != item2:
                common_sentences[item].extend(common_sentences[item2])
            if item2 not in keys:
                keys = keys + (item2,)
        sentences_matched[keys] = common_sentences[item]

    return sentences_matched


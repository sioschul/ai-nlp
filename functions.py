import itertools
import operator

import gensim
import re

import nltk
import spacy
from collections import Counter

language = ''
min_occ= 0

# read and tokenize book
def read_and_tokenize(book):
    # read whole book
    with open(book) as f:
        text = f.read()
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
        spacy_stopwords = spacy.lang.de.stop_words.STOP_WORDS
        spacy_stopwords.add('ja')
        spacy_stopwords.add('nein')
        spacy_stopwords.add('yeah')
        spacy_stopwords.add('hey')
    if language == 'es':
        spacy.load('es_core_news_sm')
        spacy_stopwords = spacy.lang.es.stop_words.STOP_WORDS
        spacy_stopwords.add('sí')
        spacy_stopwords.add('no')
        spacy_stopwords.add('yeah')
        spacy_stopwords.add('hey')
    if language == 'fr':
        spacy.load('fr_core_news_sm')
        spacy_stopwords = spacy.lang.fr.stop_words.STOP_WORDS
        spacy_stopwords.add('oui')
        spacy_stopwords.add('non')
        spacy_stopwords.add('yeah')
        spacy_stopwords.add('hey')
    if language == 'pt':
        spacy.load('pt_core_news_sm')
        spacy_stopwords = spacy.lang.pt.stop_words.STOP_WORDS
        spacy_stopwords.add('sim')
        spacy_stopwords.add('não')
        spacy_stopwords.add('yeah')
        spacy_stopwords.add('hey')
    if language == 'it':
        spacy.load('it_core_news_sm')
        spacy_stopwords = spacy.lang.it.stop_words.STOP_WORDS
        spacy_stopwords.add('sì')
        spacy_stopwords.add('no')
        spacy_stopwords.add('yeah')
        spacy_stopwords.add('hey')
    return spacy_stopwords


def load_honorifics(language):
    if language == 'en':
        honorifics = ['Master', 'Mr', 'Mr.', 'Mrs', 'Mrs.', 'Miss', 'Ms', 'Ms.', 'Mister', 'Mx', 'Mx.', 'Sir', 'Madam',
                      'Lord', 'Lady',
                      'Dr', 'Dr.', 'Doctor', 'Prof', 'Prof.', 'Professor', 'Reverend']
    if language == 'de':
        honorifics = ['Meister', 'Herr', 'Frau', 'Fräulein', 'Madam',
                      'Dr', 'Dr.', 'Doktor', 'Prof', 'Prof.', 'Professor', 'Professorin']
    if language == 'es':
        honorifics = ['Maestro', 'Señor', 'Caballero ', 'Sr.','Sr','Señora', 'Sra.','Sra', 'Señorita', 'Srta', 'Srta.',
                      'Don', 'Doña',
                      'Dr', 'Dr.', 'Doctor','Doctora', 'Prof', 'Prof.', 'Profesor','Profesora']
    if language == 'fr':
        honorifics = ['Maître', 'Me','Me.', 'Monsieur', 'M.', 'M', 'Madame', 'Mme', 'Mme.', 'Mademoiselle', 'Mlle', 'Mlle.',
                      'Dr', 'Dr.', 'Docteur','Docteure', 'Prof', 'Prof.', 'Professeur', 'Professeure', 'Monseigneur']
    if language == 'pt':
        honorifics = ['Mestre', 'Senhor', 'Sr.','Sr', 'Senhora', 'Sra.', 'Sra', 'Seu',
                      'Don', 'Dona',
                      'Dr', 'Dr.', 'Doutor','Doutora', 'Prof', 'Prof.', 'Professor','Professora']
    if language == 'it':
        honorifics = ['Maestro','Maestra', 'Signore', 'Signora',
                      'Dr', 'Dr.', 'Dottore', 'Dottoressa', 'Prof', 'Prof.', 'Professore','Professoressa' 'Don']
    return honorifics


# extracting entities and related sentences
def entity_extraction(sentences, lang, min_occurence=6):
    global language
    global min_occ
    min_occ = min_occurence
    entities_for_cooc = []
    language = lang
    tokens = []
    sentences_by_ents = {}
    # load stopwords
    spacy_stopwords = load_stop_words(language)
    # load model
    nlp = spacy.load('xx_ent_wiki_sm')
    # spacy entity model
    for i, s in enumerate(sentences):
        entity_sentence = ''
        s = re.sub('\s+', ' ', s)
        s = s.replace('-',' ')
        s = s.strip()
        doc = nlp(s)
        names = []
        for ent in doc.ents:
            name = ent.text.strip()
            # replace whitespace in multi word ents with "_"
            if len(ent.text.split()) > 1:
                name = ent.text.replace(" ", "_")
            if not (not name.endswith("!") and not name.endswith("?") and not name.endswith("\'") and not name.endswith(
                    '.') and not name.endswith("\"")) or name.startswith("\""):
                name = re.sub('[\.\'\!\?\"]$', '', name)
            # remove whitespaces from ents and remove stopwords from ents
            if name.lower() not in spacy_stopwords and not name.startswith('\'') and not name.startswith(
                    '\"') and name != '':
                sentences[i] = sentences[i].replace(ent.text, name)
                names.append(name)
                entity_sentence = entity_sentence + name + ' '
        for name in names:
            # keep all sentences from the same entity together
            # assuming entities with the same name are always the same type/person in the same book
            sentences_by_ents.setdefault(name, {})[i] = sentences[i]
            # keep track of entities with their tag
            tokens.append(name)
        if entity_sentence != '':
            entities_for_cooc.append(entity_sentence)
    # remove unnecessary entries with <6 occurrences4
    c = Counter(tokens)
    most_common = {k: c[k] for k in c if c[k] > min_occurence}
    common_sentences = {k: sentences_by_ents[k] for k in sentences_by_ents if len(sentences_by_ents[k]) > min_occurence}
    # reduce to list of names
    single_tokens = []
    for k in most_common.keys():
        if k not in single_tokens:
            single_tokens.append(k)
    return single_tokens, common_sentences, c, entities_for_cooc


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


'''# match entities first certain matching then fuzzy matching
def entity_matching(sentences, single_word_ents, multi_word_ents, common_sentences, accuracy, rule):
    # single word ents matched against multi word ents
    matched_ents = match_single_against_multi_word(single_word_ents, multi_word_ents)
    # ambiguous multi word ents
    ambiguous = find_ambiguous_words(matched_ents)
    # unambiguous matches and first name matches for ambiguous ones
    matched, amb = direct_matching(matched_ents, ambiguous)
    if rule == 1:
        # fuzzy matching with gensim
        matched_fuzzy = fuzzy_matching_gensim(sentences, single_word_ents, multi_word_ents, matched, amb, accuracy)
    elif rule == 2:
        # matching ambiguous entities based on entity frequency
        matched_fuzzy = frequency_matching(amb, matched, accuracy)
    elif rule == 3:
        look_around_matching(amb,sentences,common_sentences,accuracy)
        return matched
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


# returns a list of enitites that are ambiguous
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
def direct_matching(matched_ents, ambigous):
    global language
    honorifics = load_honorifics(language)
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
    # now unambiguos entities matched if there is a hind they belong together
    delete =[]
    for ind, m in amb.items():
        if len(m) == 1 and(m[0].startswith(ind)or m[0].endswith(ind) or ind.startswith(m[0]) or ind.endswith(m[0])):
            matched.append([ind,m[0]])
            for sl in matched:
                if sl == [ind]:
                    matched.remove(sl)
            delete.append(ind)
    for ind in delete:
        del amb[ind]
    # add remaining ambiguous entites as distinct entities
    for ind, m in matched_ents.items():
        for entry in m:
            found = False
            for sublist in matched:
                if entry in sublist:
                    found = True
                    break
            if not found:
                matched.append([entry])
    # transitivity
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


# fuzzy matching with gensim
def fuzzy_matching_gensim(sentences, single_word, multi_word, matched, amb, accuracy):
    # gensim word embedding model
    data = []
    for i in sentences:
        i = i.replace('-', ' ')
        temp = []

        # tokenize the sentence into words
        for j in nltk.word_tokenize(i):
            temp.append(j)

        data.append(temp)

    model1 = gensim.models.Word2Vec(data, min_count=2, iter=10,
                                    size=100, window=5, sg=1)
    # match ambiguos entites with most similar ones
    for ind, m in amb.items():
        matches = {}
        for x in m:
            if model1.wv.similarity(x, ind) > accuracy:
                matches[x] = model1.wv.similarity(x, ind)
        if len(matches) > 0:
            match = max(matches.items(), key=operator.itemgetter(1))[0]
            for sl in matched:
                if ind in sl:
                    sl.append(match)
                    if sl == [match]:
                        matched.remove(sl)
    # match each entity with the most similar other entities
    for sl in matched:
        add = []
        for x in sl:
            for m in model1.wv.most_similar(x):
                if (m[0] in single_word or m[0] in multi_word) and m[0] not in sl:
                    if m[1] > accuracy:
                        add.append(m[0])
        sl.extend(add)

    # remove duplicate lists
    for idx, sublist in enumerate(matched):
        temp = list(dict.fromkeys(sublist))
        temp.sort()
        matched[idx] = temp
    matched.sort()
    matched1 = list(matched for matched, _ in itertools.groupby(matched))
    return matched1

    # gensim word embedding model
    data = []
    for i in sentences:
        i = i.replace('-', ' ')
        temp = []

        # tokenize the sentence into words
        for j in nltk.word_tokenize(i):
            temp.append(j)

        data.append(temp)

    model1 = gensim.models.Word2Vec(data, min_count=2, iter=10,
                                    size=100, window=5, sg=1)
    # match ambiguos entites with most similar ones
    for ind, m in amb.items():
        matches = {}
        for x in m:
            if model1.wv.similarity(x, ind) > accuracy:
                matches[x] = model1.wv.similarity(x, ind)
        if len(matches) > 0:
            match = max(matches.items(), key=operator.itemgetter(1))[0]
            for sl in matched:
                if ind in sl:
                    sl.append(match)
                    if sl == [match]:
                        matched.remove(sl)
    # match each entity with the most similar other entities
    for sl in matched:
        add = []
        for x in sl:
            for m in model1.wv.most_similar(x):
                if (m[0] in single_word or m[0] in multi_word) and m[0] not in sl:
                    if m[1] > accuracy:
                        add.append(m[0])
        sl.extend(add)

    # remove duplicate lists
    for idx, sublist in enumerate(matched):
        temp = list(dict.fromkeys(sublist))
        temp.sort()
        matched[idx] = temp
    matched.sort()
    matched1 = list(matched for matched, _ in itertools.groupby(matched))
    return matched1
# match single words that are matched to multiple multi word entities to the most frequent one
def frequency_matching(amb, matched, entity_frequency, accuracy):
    for ind, m in amb.items():
        freq = accuracy
        match = ''
        for x in m:
            # frequency of x is frequency of x + frequency of matches before
            freq_x = 0
            for sl in matched:
                if x in sl:
                    for j in sl:
                        freq_x += entity_frequency[j]
            if freq_x > freq:
                    freq = freq_x
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
            if sl != sl2 and  not set(sl).isdisjoint(sl2):
                sl.extend(sl2)

    # remove duplicate lists
    for idx, sublist in enumerate(matched):
        temp = list(dict.fromkeys(sublist))
        temp.sort()
        matched[idx] = temp
    matched.sort()
    matched1 = list(matched for matched, _ in itertools.groupby(matched))
    return matched1

def look_around_matching(amb, sentences, common_sentences, accuracy):
    for ind, m in amb.items():
        print('before')
        print(str(ind)+':'+str(len(common_sentences[ind])))
        for x in m:
            print(str(x) + ':' + str(len(common_sentences[x])))
        # for each sentence in the ambiguous entities sentences search that sentence in the book
        for s in common_sentences[ind]:
            for ind1, se in enumerate(sentences):
                if s == se:
                    count_mentions = []
                    for i in range(accuracy):
                        if ind1+i+1 <len(sentences):
                            s1 = sentences[ind1+i+1]
                        else:
                            s1 =''
                        if ind1-i-1 >0:
                            s2= sentences[ind1-i-1]
                        else:
                            s2=''
                        for x in m:
                            for word in s1.split(' '):
                                if word == x:
                                    count_mentions.append(x)
                            for word in s2.split(' '):
                                if word == x:
                                    count_mentions.append(x)
                    count=Counter(count_mentions)
                    if count != Counter() and len(set(count.values()))== len(count.values()):
                        max_c = max(count.items(), key=operator.itemgetter(1))[0]
                        common_sentences[max_c].append(s)
                        common_sentences[ind].remove(s)
                    break
        print('after')
        print(str(ind)+':'+str(len(common_sentences[ind])))
        for x in m:
            print(str(x) + ':' + str(len(common_sentences[x])))
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

    return sentences_matched'''

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
    common_sentences = {k: sentences_by_ents[k] for k in sentences_by_ents if len(sentences_by_ents[k]) > min_occurence}
    # reduce to list of names
    single_tokens = []
    for k in c.keys():
        if k not in single_tokens and k in common_sentences.keys():
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

def get_sentences_for_summary(current_line, current_entity, sentences_by_ent, sentences):
    current_line = current_line.replace('-', ' ')
    current_line = current_line.strip()
    current_line = re.sub('\s+', ' ', current_line)
    current_ind = 0
    for ind, s in enumerate(sentences):
        s = s.replace('_', ' ')
        if s == current_line:
            current_ind = ind
            break
    for_summary = []
    for x in sentences_by_ent.keys():
        if current_entity in x:
            for i, sent in sentences_by_ent[x].items():
                if i <= current_ind:
                    for_summary.append(sent.strip())
    return for_summary

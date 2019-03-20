import itertools

import spacy
# import string
import nltk
from collections import Counter, OrderedDict
import pprint as pp
import re
import gensim
from difflib import get_close_matches, SequenceMatcher
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


# load model
nlp = spacy.load('xx_ent_wiki_sm')

# for stop word filtering
spacy.load('en')
spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
spacy_stopwords.add('yes')
spacy_stopwords.add('no')
spacy_stopwords.add('yeah')

# read book
with open("Harry_Potter_and_the_Sorcerer.txt") as f:
    book = f.read()
# split book into sentences
sentences = nltk.tokenize.sent_tokenize(book)
tokens = []
sentences_by_ents = {}

# spacy entity model
for s in sentences:
    s = re.sub('\s+', ' ', s)
    s = s.strip()
    doc = nlp(s)
    for ent in doc.ents:
        # remove whitespaces from ents and remove stopwords from ents
        if ent.text.lower() not in spacy_stopwords and not ent.text.startswith('\'') and not ent.text.startswith('\"'):
            # keep all sentences from the same entity together
            # assuming entities with the same name are always the same type/person in the same book
            sentences_by_ents.setdefault(ent.text, []).append(s)
            # keep track of entities with their tag
            tokens.append((ent.text, ent.label_))
c = Counter(tokens)
# remove unnecessary entries with <6 occurrences
most_common = {k: c[k] for k in c if c[k] > 6}
common_sentences = {k: sentences_by_ents[k] for k in sentences_by_ents if len(sentences_by_ents[k]) > 6}
# remove doubles from most_common
singles = []
for k in most_common.keys():
    if k[0] not in singles:
        singles.append(k[0])
singles.sort()
pp.pprint(singles)

matched = []
for ent in singles:
    matches = []
    for item in singles:
        if fuzz.ratio(ent, item) > 62:
       #if SequenceMatcher(None, ent, item).ratio() > 0.64:
           matches.append(item)
    #matches = get_close_matches(ent, singles, 8, 0.65)
    matched.append(matches)
for sublist in matched:
    sublist.sort()
matched.sort()
matched = list(matched for matched,_ in itertools.groupby(matched))
pp.pprint(matched)

# gensim word embedding model
data = []
for i in sentences:
    temp = []

    # tokenize the sentence into words
    for j in nltk.word_tokenize(i):
        temp.append(j)

    data.append(temp)

model1 = gensim.models.Word2Vec(data, min_count=3,
                                size=100, window=5, sg=1)
print("Harry + Voldemort ",
      model1.wv.similarity('Voldemort', 'Harry'))
print("Voldemort + You-know-who",
      model1.wv.similarity('Voldemort', 'You-Know-Who'))

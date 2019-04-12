import itertools
from collections import Counter

import spacy
import nltk

import pprint as pp
import re

# load model
nlp = spacy.load('xx_ent_wiki_sm')

# for stop word filtering
spacy.load('en')
spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
spacy_stopwords.add('yes')
spacy_stopwords.add('no')
spacy_stopwords.add('yeah')

# read book
with open("Harry_Potter_and_the_Order.txt") as f:
    book = f.read()

# split book into sentences
sentences = nltk.tokenize.sent_tokenize(book)
tokens = []
sentences_by_ents = {}
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
        # remove whitespaces from ents and remove stopwords from ents
        if name.lower() not in spacy_stopwords and not name.startswith('\'') and not name.startswith('\"'):
            # keep all sentences from the same entity together
            # assuming entities with the same name are always the same type/person in the same book
            sentences_by_ents.setdefault(name, []).append(sentences[i].strip())
            # keep track of entities with their tag
            tokens.append(name)
c = Counter(tokens)
# remove unnecessary entries with <6 occurrences
most_common = {k: c[k] for k in c if c[k] > 6}
common_sentences = {k: sentences_by_ents[k] for k in sentences_by_ents if len(sentences_by_ents[k]) > 6}
# reduce list to names
singles = []
for k in most_common.keys():
    if k not in singles:
        singles.append(k)
# divide into single and multi word
single_word_ents = []
multi_word_ents = []
for i in singles:
    if "_" in i:
        multi_word_ents.append(i)
    else:
        single_word_ents.append(i)

# matching non ambiguos + first names:
matched_ents = {}
for i in single_word_ents:
    belong_together = []
    for j in multi_word_ents:
        if i in j:
            belong_together.append(j)
    if i not in matched_ents.keys():
        matched_ents[i]=belong_together
amb=[]
for ind, m in matched_ents.items():
    for ind2, m2 in matched_ents.items():
        for i in m:
            for j in m2:
                if i == j and not ind == ind2 and j not in amb:
                    amb.append(j)
matched = []
for ind, m in matched_ents.items():
    belong_together = [ind]
    for entry in m:
        if entry not in amb:
            belong_together.append(entry)
        else:
            if entry.startswith(ind):
                belong_together.append(entry)
    if len(belong_together) > 1:
        matched.append(belong_together)
'''# match single words against multi words only first name
matched = []
for ent in single_word_ents:
    belong_together = [ent]
    for i in multi_word_ents:
        if i.startswith(ent):
            belong_together.append(i)
    if len(belong_together) > 1:
        matched.append(belong_together)'''
'''for ent in single_word_ents:
    belong_together = [ent]
    for i in single_word_ents:
        if ent == i +'s':
            belong_together.append(i)
    if len(belong_together) > 1:
        extended = False
        for sublist in matched:
            for x in belong_together:
                if x in sublist:
                    sublist.extend(belong_together)
                    extended = True
        if not extended:
            matched.append(belong_together'''
matched.sort()
pp.pprint(matched)

#put sentences togther passed on matched entities
sentences_matched ={}
for sublist in matched:
    keys = ()
    for item in sublist:
        for item2 in sublist:
            value = common_sentences[item].extend(common_sentences[item2])
            if item2 not in keys:
                keys = keys +(item2,)
    sentences_matched[keys] = common_sentences[item]

#remove duplicates
for key, value in sentences_matched.items():
    new_sentences = list(dict.fromkeys(value))
    new_sentences.sort()
    sentences_matched.update({key : new_sentences})

sentences_clear = {}
for key,value in sentences_matched.items():
    if value not in sentences_clear.values():
        sentences_clear[key] = value


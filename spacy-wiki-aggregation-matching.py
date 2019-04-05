import itertools
from collections import Counter

import spacy
# import string
import nltk

import pprint as pp
import re
import gensim
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
#ents =[]
# spacy entity model
for i, s in enumerate(sentences):
    s = re.sub('\s+', ' ', s)
    s = s.strip()
    doc = nlp(s)
    for ent in doc.ents:
        name = ent.text
        if len(ent.text.split()) > 1:
            name = ent.text.replace(" ", "_")
            sentences[i] = sentences[i].replace(ent.text, name)
        # remove whitespaces from ents and remove stopwords from ents
        if name.lower() not in spacy_stopwords and not name.startswith('\'') and not name.startswith('\"'):
            # keep all sentences from the same entity together
            # assuming entities with the same name are always the same type/person in the same book
            sentences_by_ents.setdefault(name, []).append(sentences[i].strip())
            # keep track of entities with their tag
            tokens.append((name, ent.label_))
            #ents.append(ent)

'''for ent in ents:
    if ent.text =='Harry':
        ent1 = ent
        break
for ent in ents:
    if ent.text == 'Harry Potter':
        ent2 = ent
        break
print(ent1.similarity(ent2)) ca. 0.6'''
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
#pp.pprint(singles)

# match entities which are substrings of each other
matched= []
for ent in singles:
    belong_together = []
    for i in singles:
        if i in ent or ent in i:
            belong_together.append(i)
    extended = False
    for sublist in matched:
        for x in belong_together:
            if x in sublist:
                sublist.extend(belong_together)
                extended = True
    if not extended:
        matched.append(belong_together)

# remove duplicates from matches
for idx ,sublist in enumerate(matched):
    temp = list(dict.fromkeys(sublist))
    temp.sort()
    matched[idx]=temp
matched.sort()
matched = list(matched for matched,_ in itertools.groupby(matched))
#pp.pprint(matched)

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

#pp.pprint(sentences_clear)

#print(sentences_clear["Dumbledore"])
# matching with substring
#for ent in singles:
    #together = []
    #for k in singles:
        #if ent in k:
            #together.append(k)
        #appended = False
        #for sublist in matched:
            #for item in together:
                #if item in sublist:
                    #for i in together:
                        #if i not in sublist:
                            #sublist.append(i)
                            #appended = True
    #if not appended:
        #matched.append(together)

#for sublist in matched:
    #sublist.sort()
#matched.sort()
#matched = list(matched for matched,_ in itertools.groupby(matched))


# gensim word embedding model
data = []
for i in sentences:
    temp = []

    # tokenize the sentence into words
    for j in nltk.word_tokenize(i):
        temp.append(j)

    data.append(temp)

model1 = gensim.models.Word2Vec(data, min_count=2, hs=0, iter=8,
                                size=100, window=5, sg=1)
print("Harry")
print("Harry_Potter",model1.wv.similarity('Harry', 'Harry_Potter'))
for x in model1.wv.most_similar('Harry'):
    if x[0] in singles:
        print(x)
print("Harry_Potter",
      model1.wv.most_similar('Harry_Potter'))
print("Voldemort",
      model1.wv.most_similar('Voldemort'))


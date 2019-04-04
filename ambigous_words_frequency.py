import itertools
import re
import pprint as pp
import nltk
import spacy
from collections import Counter

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
            # keep track of entities with their tag
            tokens.append(name)
c = Counter(tokens)
# remove unnecessary entries with <6 occurrences
most_common = {k: c[k] for k in c if c[k] > 6}
single_word_ents = []
multi_word_ents = []
for i in tokens:
    if i in most_common.keys():
        if "_" in i:
            multi_word_ents.append(i)
        else:
            single_word_ents.append(i)
'''
matched_ents = {}
for i in single_word_ents:
    belong_together = []
    for j in multi_word_ents:
        if i in j:
            belong_together.append(j)
    if i not in matched_ents.keys():
        matched_ents[i]=belong_together
#pp.pprint(matched_ents['Harry'])
for ind, sublist in matched_ents.items():
    c=Counter(sublist)
    matched_ents[ind]=c
delete = [key for key, sub in matched_ents.items() if sub == Counter()]
for key in delete:
    del matched_ents[key]
#pp.pprint(matched_ents)
singles_single = []
for k in single_word_ents:
    if k not in singles_single:
        singles_single.append(k)
singles_multi = []
for k in multi_word_ents:
    if k not in singles_multi:
        singles_multi.append(k)'''
matched_ents_2 = []
for ent in single_word_ents:
    belong_together = [ent]
    for i in multi_word_ents:
        if ent in i:
            belong_together.append(i)
    appended = False
    for sublist in matched_ents_2:
        for x in belong_together:
            if x in sublist:
                sublist.extend(belong_together)
                appended = True
    if not appended:
        matched_ents_2.append(belong_together)
#pp.pprint(matched_ents_2)
matched_ents_trans=[]
for ind,i in enumerate(matched_ents_2):
    c=Counter(i)
    if c != Counter() and len(c.items()) > 1:
        matched_ents_trans.append(c)
pp.pprint(matched_ents_trans)
'''for idx ,sublist in enumerate(matched_ents_2):
    temp = list(dict.fromkeys(sublist))
    temp.sort()
    matched_ents_2[idx]=temp
matched_ents_2.sort()
matched_ents_trans = list(matched for matched,_ in itertools.groupby(matched_ents_2))
pp.pprint(matched_ents_trans)'''

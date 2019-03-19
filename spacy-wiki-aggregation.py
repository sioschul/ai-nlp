import spacy
# import string
import nltk
from collections import Counter, OrderedDict
import pprint as pp
import re
import gensim
from difflib import get_close_matches, SequenceMatcher

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

# sort same named entities with different tags together
# make all entries have the most common tag, which is not MISC
done = []
aggregated = {}
for k, v in most_common.items():
    if k[0] not in done:
        new_dict = {k: v}
        for k1, v1 in most_common.items():
            if k1[0] == k[0] and k1 != k:
                new_dict[k1] = v1
                sorted_dict = OrderedDict(sorted(new_dict.items(), key=lambda kv: kv[1], reverse=True))
                keys = list(sorted_dict.keys())
                items = list(sorted_dict.items())
                tag = keys[0][1]
                if len(items) > 1:
                    if keys[0][1] == "MISC":
                        tag = keys[1][1]
                        changed = {k[0]: tag}
                        aggregated.update(changed.items())
    done.append(k[0])
pp.pprint(aggregated)

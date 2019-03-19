
import spacy
import nltk
from collections import Counter, OrderedDict
import pprint as pp

# load model
nlp = spacy.load('en')

# read book
with open("Harry_Potter_and_the_Sorcerer.txt") as f:
    book = f.read()
# split book into sentences
sentences = nltk.tokenize.sent_tokenize(book)
tokens = []
sentences_by_ents = {}

for s in sentences:
    s = s.strip()
    doc = nlp(s)
    for token in doc:
        if token.pos_ == 'PROPN':
            # remove whitespaces from ents
            if "\n\n" not in token.text:
                # keep all sentences from the same entity together
                # assuming entities with the same name are always the same type/person in the same book
                sentences_by_ents.setdefault(token.text, []).append(s)
                # keep track of entities with their tag
                tokens.append((token.text, token.ent_type_))
c = Counter(tokens)
# remove unnecessary entries with <6 occurrences
most_common = {k: c[k] for k in c if c[k] > 6}
most_common_sentences = {k: sentences_by_ents[k] for k in sentences_by_ents if len(sentences_by_ents[k]) > 6}
pp.pprint(sorted(most_common.items(), key=lambda kv: kv[0]))


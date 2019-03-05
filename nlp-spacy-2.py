import spacy
from collections import Counter

nlp = spacy.load('en')
with open("HP_ch2.txt") as f:
    book = f.read()
doc = nlp(book)
tokens = []
for ent in doc.ents:
    tokens.append((ent.text, ent.label_))
c = Counter(tokens)
print(c.most_common(24))
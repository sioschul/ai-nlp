import spacy
from collections import Counter

nlp = spacy.load('en')
with open("HP_ch2.txt") as f:
    book = f.read()
doc = nlp(book)
words=[]
for x in doc:
    if x.ent_type_ != '':
        words.append((str(x), x.ent_type_))
c = Counter(words)
print(c.most_common(24))

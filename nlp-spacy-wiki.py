import spacy
import nltk
from collections import Counter

nlp = spacy.load('xx_ent_wiki_sm')
with open("Harry_Potter_and_the_Sorcerer.txt") as f:
    book = f.read()
sentences = nltk.tokenize.sent_tokenize(book)
tokens = []
for s in sentences:
    doc = nlp(s)
    for ent in doc.ents:
        tokens.append((ent.text, ent.label_))
c = Counter(tokens)
print(c.most_common(24))
#with open("entites_HP1_wikimodel.txt", "a") as f:
    #f.write(str(c))


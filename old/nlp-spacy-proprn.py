import nltk
import spacy
from collections import Counter

nlp = spacy.load('en')
with open("HP_ch1.txt") as f:
    book = f.read()
sentences = nltk.tokenize.sent_tokenize(book)
propn = []
for s in sentences:
    doc = nlp(s)
    for token in doc:
        if token.pos_ == 'PROPN':
            #if token.ent_iob_ != 'O':
            # if token.text == 'Fancy':
               # print(s)
            propn.append((token.text, token.pos_, token.ent_type_))
c = Counter(propn)
#print(c)
print(c.most_common(24))
#with open("HP_PROPN_mostcommon.txt", "a") as f:
    #for x in c.most_common(24):
        #f.write(str(x) + '\n')

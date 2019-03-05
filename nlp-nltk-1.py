import nltk
from collections import Counter
nltk.download('words')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('maxent_ne_chunker')

def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

with open("HP_ch1.txt") as f:
    book = f.read()
sent = preprocess(book)
nnp = []
for token in sent:
    if token[1] == 'NNP':
        nnp.append(token)
#print(nnp)
#c = Counter(nnp)
#print(c.most_common(24))
#print(sent)
tree = nltk.ne_chunk(nnp)
print(tree)
#c = Counter(tree)
#print(c.most_common(24))
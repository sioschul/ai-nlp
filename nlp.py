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
        #if ent.text == 'Harry':
        #if ent.label_ == 'PERSON':
        #      with open("HP_Person.txt", "a") as f:
        #                f.write(s + "\n")
        # if ent.label_ == 'ORG':
        #         with open("HP_ORG.txt", "a") as f:
        #                 f.write(s + "\n")
        #if ent.label_ == 'GPE':
        #        with open("HP_GPE.txt", "a") as f:
        #        f.write(s + "\n")
        #if ent.label_ == 'NORP':
        #        with open("HP_NORP.txt", "a") as f:
        #    f.write(s + "\n")
        # if ent.label_ == 'WORK_OF_ART':
        # with open("HP_WOA.txt", "a") as f:
        #         f.write(s + "\n")
        #if ent.text == 'Snape':
        #if ent.label_ == 'LOC':
        #     with open("Snape_LOC.txt", "a") as f:
        #       f.write(s + "\n\n")
        # if ent.label_ == 'ORG':
        #         with open("Snape_ORG.txt", "a") as f:
        #                 f.write(s + "\n\n")
        # if ent.label_ == 'GPE':
        #          with open("Snape_GPE.txt", "a") as f:
        #                 f.write(s + "\n\n")
        # if ent.label_ == 'PERSON':
        #        with open("Snape_PERSON.txt", "a") as f:
        #                f.write(s + "\n\n")
        #if ent.label_ == 'NORP':
        #        with open("Snape_NORP.txt", "a") as f:
        #                f.write(s + "\n\n")
        tokens.append((ent.text, ent.label_))
c = Counter(tokens)
print(c.most_common(24))

import codecs
import pprint as pp
import re
import minie_process as mp

import functions as fn
import entity_matching as em

# language of the book
language = 'en'
# read and tokenize books
sentences = fn.read_and_tokenize("Harry_Potter_and_the_Sorcerer.txt")

# extract entities
# @param: sentences, language and optional min_coccurrence to consider
# @return: list with unique entity names, dict with all sentences belonging to one entity (key=entity name),
#         dict of entity with their frequency in the book, coocurrence matrix
single_tokens, common_sentences, entity_frequency, cooc = fn.entity_extraction(sentences, language, 6)

# distinguish into single and multi word entities
single_word_ents, multi_word_ents = fn.divide_into_single_and_multi_word(single_tokens)

# non-fuzzy matching, based on several rules
# @param: single word entities, multi word entities and language
# @return: list of lists of matched entities, dict of still ambiguous entities and the possible options
matched, amb = em.non_fuzzy_entity_matching(single_word_ents, multi_word_ents, language)

# fuzzy matching with majority vote consisting of: gensim word embedding, overall entity frequency,
# entity frequency before, entity frequency after, coocurence
# @param: dict of still ambiguous entities and the possible options, matched entities so far, overall entity frequency,
#         dict with all sentences belonging to one entity, coocurence matrix, single word entities,
#         multi word entities, min accuracy for gensim model, min over all frequency to consider,
#         number of sentences to look at before and after each entity mention
# @return: new dict of sentences matched to entities, where each decidable ambiguous entity mention is moved to the
#            section of the entity it has been allocated to
fuzzy_sentences = em.fuzzy_entity_matching(amb, matched, sentences, entity_frequency, common_sentences, cooc,
                                           single_word_ents, multi_word_ents, accuracy_gensim=0.4,
                                           accuracy_frequency=6, accuracy_lookaround=3)
new_common_sentences = em.sort_sentences_to_matched_entities(fuzzy_sentences, matched)
# replace different entity names in the sentences by the longest matched entity name
'''for i,x in new_common_sentences.items():
    longest_name= max(i,key=len)
    for k, v in x.items():
        for name in i:
            if name != longest_name:
                x[k] = v.replace(name, longest_name)'''
# line we are currently
current_line = 'The clanging and crashing were enough to wake the whole castle.'
current_entity = 'Professor_McGonagall'
# get the sentences about the current entity that have been read so far
# @param: line we are currently in, entity name we want to summarize, sentences sorted by entitiies, all sentences
# @return: list of sentences that can be used for summary without spoilers
summary_sentences, target_tuple = fn.get_sentences_for_summary(current_line, current_entity, new_common_sentences, sentences)
mp.minie_processing(summary_sentences, current_entity, target_tuple)
'''with open('minie1.txt','w+', newline='') as f:
    f.write("\n".join(summary_sentences))
with open('minie1.txt','r+') as file:
    with open('minie.txt','w+') as f:
        lines = file.readlines()
        for line in lines:
            if line.strip() and len(line.strip())!=1:
                f.write(line)'''

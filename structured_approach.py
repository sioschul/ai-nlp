import codecs
import pprint as pp

import functions as fn
import entity_matching as em
# line we are currently
#current_sentence = 'I\'m going to have a lot of fun with Dudley this summer....\"'
#current_sentence = 'Instead, he smiled, raised a hand in farewell, turned around and led the way out of the station towards the sunlit street, with Uncle Vernon, Aunt Petunia and Dudley hurrying along in his wake. '
#current_sentence='Harry set off toward the station exit, Hedwig rattling along in front of him, for what looked like a much better summer than the last.'
#current_sentence ='And that is the very end of the adventures of the wardrobe. But if the Professor was right it was only the beginning of the adventures of Narnia.'
language='de'
# read and tokenize books
sentences = fn.read_and_tokenize("got_ger.txt")
# extract entities
# param: sentences, language and optional min_coccurrence to consider
# result: list with entity names, dict with all sentences belonging to one entity (key=entity name)
single_tokens, common_sentences, entity_frequency, cooc = fn.entity_extraction(sentences, language, 0)
# distinguish into single and multi word entites
single_word_ents, multi_word_ents = fn.divide_into_single_and_multi_word(single_tokens)
matched, amb = em.non_fuzzy_entity_matching(single_word_ents,multi_word_ents,language)
#pp.pprint(matched)
new_common_sentences = em.fuzzy_entity_matching(amb, matched, sentences, entity_frequency, common_sentences, cooc,
                                                single_word_ents,multi_word_ents, accuracy_gensim=0,
                                                accuracy_frequency=0, accuracy_lookaround=3)








''''# entity matching
# param: single word entites, multi word entites, threshold for fuzzy matching
# rule for fuzzy matching
# 0 = no fuzzy matching
# 1 = gensim accurracy = min accuracy to consider
# 2 = matching based on most frequent words accuracy = min occurence to consider
# 3 = matching based on neighbors accuracy = number of sentences around to look at
matched = fn.entity_matching(sentences, single_word_ents, multi_word_ents, common_sentences, 3, 0)
# match sentences of matched entities together
sentences_clear = fn.sort_sentences_to_matched_entities(common_sentences, matched)'''



import pprint as pp

import functions as fn

# line we are currently
current_sentence = 'I\'m going to have a lot of fun with Dudley this summer....\"'
#current_sentence = 'Instead, he smiled, raised a hand in farewell, turned around and led the way out of the station towards the sunlit street, with Uncle Vernon, Aunt Petunia and Dudley hurrying along in his wake. '


# read and tokenize book
sentences = fn.read_and_tokenize("Harry_Potter_and_the_Sorcerer.txt", current_sentence)

# extract entities
# param: sentences, language and optional min_coccurrence to consider
# result: list with entity names, dict with all sentences belonging to one entity (key=entity name)
single_tokens, common_sentences = fn.entity_extraction(sentences, 'en')
# distinguish into single and multi word entites
single_word_ents, multi_word_ents = fn.divide_into_single_and_multi_word(single_tokens)

# entity matching
# param: single word entites, multi word entites, threshold for fuzzy matching, rule for fuzzy matching 0=no fuzzy matching, 1=gensim
matched = fn.entity_matching(sentences, single_word_ents, multi_word_ents, 0.98, 0)

# match sentences of matched entities together
sentences_clear = fn.sort_sentences_to_matched_entities(common_sentences, matched)
#pp.pprint(sentences_clear.keys())

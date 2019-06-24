from flask import Flask, render_template
import minie_process as mp
import functions as fn
import entity_matching as em
from nltk import sent_tokenize

app = Flask(__name__)
language = 'en'
sentences = []
new_common_sentences={}
sentences_to_display =[]


# routes for GET requests rendering pages
@app.route('/')
def starting_page():
    global sentences, new_common_sentences, sentences_to_display
    sentences = []
    new_common_sentences = {}
    sentences_to_display = []
    return render_template('starting_page.html')

@app.route('/select')
def point_in_book():
    return render_template('select_point.html')

@app.route('/display')
def display_sentences():
    return render_template('display_book.html')

@app.route('/graph')
def display_graph():
    return render_template('display_graph.html')

#load the selected book from prepared files
@app.route('/load-book/<number>', methods=['GET', 'POST'])
def load_book(number):
    global sentences, new_common_sentences
    book_number = int('%s' % number)
    if book_number == 1:
        sentences = fn.read_and_tokenize("Harry_Potter_and_the_Sorcerer.txt")
        with open('HP1.txt', 'r') as f:
            ex = f.read()
            new_common_sentences = eval(ex)
        return '1'
    elif book_number == 2:
        sentences = fn.read_and_tokenize("Harry_Potter_and_the_Chamber.txt")
        with open('HP2.txt', 'r') as f:
            ex = f.read()
            new_common_sentences = eval(ex)
        return '1'
    elif book_number == 3:
        sentences = fn.read_and_tokenize("Harry_Potter_and_the_Prisoner.txt")
        with open('HP3.txt', 'r') as f:
            ex = f.read()
            new_common_sentences = eval(ex)
        return '1'
    elif book_number == 4:
        sentences = fn.read_and_tokenize("Harry_Potter_and_the_Order.txt")
        with open('HP4.txt', 'r') as f:
            ex = f.read()
            new_common_sentences = eval(ex)
        return '1'
    else:
        return '-1'

# process users text
@app.route('/owntext/<text>',methods=['GET', 'POST'])
def process_owntext(text):
    global sentences, new_common_sentences, sentences_to_display, language
    input_text = '%s' % text
    sentences = sent_tokenize(input_text)
    single_tokens, common_sentences, entity_frequency, cooc = fn.entity_extraction(sentences, language, 0)
    single_word_ents, multi_word_ents = fn.divide_into_single_and_multi_word(single_tokens)
    matched, amb = em.non_fuzzy_entity_matching(single_word_ents, multi_word_ents, language)
    fuzzy_sentences = em.fuzzy_entity_matching(amb, matched, sentences, entity_frequency, common_sentences, cooc,
                                               single_word_ents, multi_word_ents, accuracy_gensim=0.4,
                                               accuracy_frequency=2, accuracy_lookaround=1)
    new_common_sentences = em.sort_sentences_to_matched_entities(fuzzy_sentences, matched)
    sentences_to_display = sentences
    return '1'


# find sentences around a given percentage of the book
@app.route('/point-book/<point>', methods=['GET', 'POST'])
def point_book(point):
    global sentences, sentences_to_display
    book_point = int('%s' % point)/100
    total = len(sentences)
    line_at_point = round(total*book_point)
    upper = line_at_point + 10
    lower = line_at_point - 10
    # check for bounds
    if upper > total-1:
        upper = total-1
    if lower < 0:
        lower = 0
    for ind, sen in enumerate(sentences):
        if lower <= ind <= upper:
            sentences_to_display.append(sen)
    return '1'

# get the selected sentences to display
@app.route('/load-display-text')
def load_display_text():
    sent = ''
    for x in sentences_to_display:
        sent = sent + x.replace('\n', ' ') + '+;'
    return sent

# get the entities found in book to display
@app.route('/load-entities')
def load_entities():
    global new_common_sentences
    keys = new_common_sentences.keys()
    sent = ''
    for x in keys:
        for y in x:
            sent = sent + y + ','
    return sent

# generate the minie output graph given a entity and the point in the book/sentences regarding this entity
@app.route('/generate-graph/<entity>/<sentence>')
def generate_graph(entity, sentence):
    global new_common_sentences, sentences
    current_entity = '%s' % entity
    current_line = '%s' % sentence
    summary_sentences, target_tuple = fn.get_sentences_for_summary(current_line, current_entity, new_common_sentences, sentences)
    # save the picture locally, as '/graphs/' + center + '.png'
    df, path = mp.minie_processing(summary_sentences, target_tuple)
    return path

if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)

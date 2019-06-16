from flask import Flask, render_template
import minie_process as mp
import functions as fn
import entity_matching as em

app = Flask(__name__)
language = 'en'
sentences = []
new_common_sentences={}
sentences_to_display =[]

# routes for GET requests rendering pages
@app.route('/')
def starting_page():
    return render_template('starting_page.html')

@app.route('/select')
def point_in_book():
    return render_template('select_point.html')

@app.route('/display')
def display_sentences():
    return render_template('display_book.html')

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

if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def starting_page():
    return render_template('starting_page.html')

@app.route('/select')
def point_in_book():
    return render_template('select_point.html')


if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)

import spacy

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
spacy.load('en')
stopwords = spacy.lang.en.stop_words.STOP_WORDS
stopwords.add('yes')
stopwords.add('no')
stopwords.add('yeah')

def show_wordcloud(data, title = None):
    wordcloud = WordCloud(
        background_color='white',
        stopwords=stopwords,
        max_words=200,
        max_font_size=40,
        scale=3,
        random_state=1  # chosen at random by flipping a coin; it was heads
    ).generate(str(data))

    fig = plt.figure(1, figsize=(12, 12))
    plt.axis('off')
    if title:
        fig.suptitle(title, fontsize=20)
        fig.subplots_adjust(top=2.3)

    plt.imshow(wordcloud)
    plt.show()


if __name__ == '__main__':
    with open('Hermione.txt') as f:
        text_str = f.read()
    show_wordcloud(text_str)

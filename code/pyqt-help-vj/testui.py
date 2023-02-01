import sys
from PyQt5 import QtWidgets, uic, QtGui
import qdarktheme

from twitter_API import data_collator
from twitter_API.data_collator import filename_creation
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import webbrowser
import os
import re
import random
import sqlite3 as sql
import numpy as np

id2label = {
    0: "medicine",
    1: "business",
    2: "videogames",
    3: "education",
    4: "religion",
    5: "science",
    6: "philosophy",
    7: "politics",
    8: "music",
    9: "sports",
    10: "law",
    11: "culture",
    12: "economics",
    13: "geography",
    14: "technology",
    15: "mathematics",
    16: "history",
    17: "foods",
    18: "disasters",
    19: "entertainment"
}

tweet_collator = data_collator.DataCollator("./twitter_API/pass.secret", id2label, )

Ui_findTopic, _ = uic.loadUiType("findtopic2.ui")
Ui_topTopics, _ = uic.loadUiType("toptopics.ui")
Ui_wordCloud, _ = uic.loadUiType("wordcloud.ui")

def generate_wordcloud(text):
    # Create and generate a word cloud image:
    filename = filename_creation(text, "wordcloud")
    wordcloud = WordCloud(width=335, height=370).generate(text)
    # save the wordcloud
    wordcloud.to_file(filename)

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.twitter_tweetset = tweet_collator.get_twitter_tweets()
        self.your_tweetset = tweet_collator.get_tweets()
        self.twitter_ht = ["" for _ in range(5)]
        self.your_ht = ["" for _ in range(5)]

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.wordCloud()
        self.topTopics()
        self.findTopics()
        self.setCentralWidget(self.stacked_widget)
        self.resize(800,600)


    def wordCloud(self):
        self.wordCloud_widget = QtWidgets.QMainWindow()
        Ui_wordCloud().setupUi(self.wordCloud_widget)
        self.stacked_widget.addWidget(self.wordCloud_widget)
        self.button1 = self.wordCloud_widget.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button1.clicked.connect(lambda : self.goto_page(self.topTopics_widget))
        self.button1 = self.wordCloud_widget.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.button1.clicked.connect(lambda : self.goto_page(self.findTopics_widget))
        self.get_your_wordcloud()
        self.get_twitter_wordcloud()

    def gen_wordcloud(self, tweetset):
        tweets = tweet_collator.db_get_tweets(tweetset)
        text = ""
        for tweet in tweets:
            text += tweet[0]

        # remove links, and "RT"
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"RT", "", text)

        generate_wordcloud(text)

        return text


    def get_your_wordcloud(self):
        text = self.gen_wordcloud(self.your_tweetset)
        # get wordcloud.png and load into graphicsView
        self.graphicsView = self.wordCloud_widget.findChild(QtWidgets.QGraphicsView, 'graphicsView')
        self.scene = QtWidgets.QGraphicsScene()

        self.graphicsView.setScene(self.scene)

        filename = filename_creation(text, "wordcloud")
        
        self.image_qt = QtGui.QImage(filename)

        pic = QtWidgets.QGraphicsPixmapItem()
        pic.setPixmap(QtGui.QPixmap.fromImage(self.image_qt))
        self.scene.setSceneRect(0, 0, 335, 370)
        self.scene.addItem(pic)

    def get_twitter_wordcloud(self):
        text =self.gen_wordcloud(self.twitter_tweetset)

        # get wordcloud.png and load into graphicsView
        self.graphicsView = self.wordCloud_widget.findChild(QtWidgets.QGraphicsView, 'graphicsView_2')
        self.scene = QtWidgets.QGraphicsScene()

        self.graphicsView.setScene(self.scene)

        filename = filename_creation(text, "wordcloud")
        
        self.image_qt = QtGui.QImage(filename)

        pic = QtWidgets.QGraphicsPixmapItem()
        pic.setPixmap(QtGui.QPixmap.fromImage(self.image_qt))
        self.scene.setSceneRect(0, 0, 335, 370)
        self.scene.addItem(pic)


    def topTopics(self):
        self.topTopics_widget = QtWidgets.QMainWindow()
        Ui_topTopics().setupUi(self.topTopics_widget)
        self.stacked_widget.addWidget(self.topTopics_widget)
        self.button1 = self.topTopics_widget.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button1.clicked.connect(lambda : self.goto_page(self.wordCloud_widget))
        self.button2 = self.topTopics_widget.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.button2.clicked.connect(lambda : self.goto_page(self.findTopics_widget))
        your_topics = self.get_toptopics()
        twitter_topics = self.get_toptopics(yours=False)
        self.set_cosine_similarity(twitter_topics, your_topics)

        self.yours = [False for _ in range(5)]
        self.twitters = [False for _ in range(5)]

        self.topTopics_widget.findChild(QtWidgets.QToolButton, 'expy1').clicked.connect(lambda : self.show_hashtags(1, True))
        self.topTopics_widget.findChild(QtWidgets.QToolButton, 'expy2').clicked.connect(lambda : self.show_hashtags(2, True))
        self.topTopics_widget.findChild(QtWidgets.QToolButton, 'expy3').clicked.connect(lambda : self.show_hashtags(3, True))
        self.topTopics_widget.findChild(QtWidgets.QToolButton, 'expy4').clicked.connect(lambda : self.show_hashtags(4, True))
        self.topTopics_widget.findChild(QtWidgets.QToolButton, 'expy5').clicked.connect(lambda : self.show_hashtags(5, True))
        self.topTopics_widget.findChild(QtWidgets.QToolButton, 'expt1').clicked.connect(lambda : self.show_hashtags(1, False))
        self.topTopics_widget.findChild(QtWidgets.QToolButton, 'expt2').clicked.connect(lambda : self.show_hashtags(2, False))
        self.topTopics_widget.findChild(QtWidgets.QToolButton, 'expt3').clicked.connect(lambda : self.show_hashtags(3, False))
        self.topTopics_widget.findChild(QtWidgets.QToolButton, 'expt4').clicked.connect(lambda : self.show_hashtags(4, False))
        self.topTopics_widget.findChild(QtWidgets.QToolButton, 'expt5').clicked.connect(lambda : self.show_hashtags(5, False))


    def show_hashtags(self, i, yours):
        if yours:
            if not self.yours[i-1]:
                self.yours[i-1] = True
                self.topTopics_widget.findChild(QtWidgets.QLabel, f"ysub{i}").setText(self.your_ht[i-1])
            else:
                self.yours[i-1] = False
                self.topTopics_widget.findChild(QtWidgets.QLabel, f"ysub{i}").setText("")
        else:
            if not self.twitters[i-1]:
                self.twitters[i-1] = True
                self.topTopics_widget.findChild(QtWidgets.QLabel, f"tsub{i}").setText(self.twitter_ht[i-1])
            else:
                self.twitters[i-1] = False
                self.topTopics_widget.findChild(QtWidgets.QLabel, f"tsub{i}").setText("")

    def cosine_similarity(self, a, b):
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b)

    def _get_sim_text_colour(self, similarity):
        # generate an rgb scale from red to green
        r = 255*(1-similarity)
        g = 255*similarity
        b = 0
        return f"rgb({r:.0f}, {g:.0f}, {b:.0f})"

    def set_cosine_similarity(self, top_topics, yours):
        similarity = self.cosine_similarity(list(top_topics.values()), list(yours.values()))

        simlabel = self.topTopics_widget.findChild(QtWidgets.QLabel, 'similarity')
        simlabel.setText(f"{similarity*100:.1f}%")
        simlabel.setStyleSheet(f"QLabel {{font-weight: 500;letter-spacing: 0.025rem;font-style: normal;text-transform: capitalize;color: #FFFFFF;background-color: #bbbbbb; border-style:solid; border-width:5px; border-color:#b2b2b2; color: {self._get_sim_text_colour(similarity)}}}")

    def get_toptopics(self, yours=True):
        # get tweets
        if yours:
            lbl = "yl"
            prog = "yprog"
            topics = tweet_collator.db_get_top_topics(self.your_tweetset)
        else:
            lbl = "tl"
            prog = "tprog"
            topics = tweet_collator.db_get_top_topics(self.twitter_tweetset)
            
        # filter to only grab top 5 keys based on value
        top_topics = dict(sorted(topics.items(), key=lambda item: item[1], reverse=True)[:5])
        print(top_topics)
        for i, (key, value) in enumerate(top_topics.items()):
            self.topTopics_widget.findChild(QtWidgets.QLabel, f"{lbl}{i+1}").setText(key)
            self.progress = self.topTopics_widget.findChild(QtWidgets.QProgressBar, f"{prog}{i+1}").setValue(int(value*100))
            
            # get hashtags for topic in the given tweetset
            if yours:
                hashtags = tweet_collator.db_get_hashtags_for_topic(self.your_tweetset, key)
                hashtags = [h[0] for h in hashtags]
                # create map that maps hashtag to number of times it appears
                hashtags = {hashtag: hashtags.count(hashtag) for hashtag in hashtags}
                # find top 3 most common hashtags
                top_hashtags = dict(sorted(hashtags.items(), key=lambda item: item[1], reverse=True)[:3])
                #format hashtags in a string as bullet points
                try:
                    hashtags = " ".join([f"• {key}\n" for key, value in top_hashtags.items()][:3])
                except IndexError:
                    hashtags = " ".join([f"• {key}\n" for key, value in top_hashtags.items()])

                #remove last character which is a newline
                self.your_ht[i] = hashtags[:-1]
            else:
                hashtags = tweet_collator.db_get_hashtags_for_topic(self.twitter_tweetset, key)
                hashtags = [h[0] for h in hashtags]
                hashtags = {hashtag: hashtags.count(hashtag) for hashtag in hashtags}
                # find top 3 most common hashtags
                top_hashtags = dict(sorted(hashtags.items(), key=lambda item: item[1], reverse=True)[:3])
                #format hashtags in a string as bullet points
                try:
                    hashtags = " ".join([f"• {key}\n" for key, value in top_hashtags.items()][:3])
                except IndexError:
                    hashtags = " ".join([f"• {key}\n" for key, value in top_hashtags.items()])
                    
                self.twitter_ht[i] = hashtags[:-1]

        return topics
            

    def findTopics(self):
        self.findTopics_widget = QtWidgets.QMainWindow()
        Ui_findTopic().setupUi(self.findTopics_widget)
        self.stacked_widget.addWidget(self.findTopics_widget)
        self.button1 = self.findTopics_widget.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button1.clicked.connect(lambda : self.goto_page(self.wordCloud_widget))
        self.button2 = self.findTopics_widget.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.button2.clicked.connect(lambda : self.goto_page(self.topTopics_widget))

        # loop through values of id2label
        # for i, (key, value) in enumerate(id2label.items()):
        #     print(f"button: {value}button, value: {value}")
        #     self.findTopics_widget.findChild(QtWidgets.QPushButton, f"{value}button").clicked.connect(lambda : self.get_topic_tweets(value))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'medicine').clicked.connect(lambda : self.get_topic_tweets('medicine'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'business').clicked.connect(lambda : self.get_topic_tweets('business'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'videogames').clicked.connect(lambda : self.get_topic_tweets('videogames'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'education').clicked.connect(lambda : self.get_topic_tweets('education'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'religion').clicked.connect(lambda : self.get_topic_tweets('religion'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'science').clicked.connect(lambda : self.get_topic_tweets('science'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'philosophy').clicked.connect(lambda : self.get_topic_tweets('philosophy'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'politics').clicked.connect(lambda : self.get_topic_tweets('politics'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'music').clicked.connect(lambda : self.get_topic_tweets('music'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'sports').clicked.connect(lambda : self.get_topic_tweets('sports'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'law').clicked.connect(lambda : self.get_topic_tweets('law'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'culture').clicked.connect(lambda : self.get_topic_tweets('culture'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'economics').clicked.connect(lambda : self.get_topic_tweets('economics'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'geography').clicked.connect(lambda : self.get_topic_tweets('geography'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'technology').clicked.connect(lambda : self.get_topic_tweets('technology'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'mathematics').clicked.connect(lambda : self.get_topic_tweets('mathematics'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'history').clicked.connect(lambda : self.get_topic_tweets('history'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'foods').clicked.connect(lambda : self.get_topic_tweets('foods'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'disasters').clicked.connect(lambda : self.get_topic_tweets('disasters'))
        self.findTopics_widget.findChild(QtWidgets.QPushButton, 'entertainment').clicked.connect(lambda : self.get_topic_tweets('entertainment'))

    def clear_table(self):
        # set all "tweet{i}" labels to empty string
        for i in range(1, 5):
            self.findTopics_widget.findChild(QtWidgets.QLabel, f"tweet{i}").setText("")
            self.findTopics_widget.findChild(QtWidgets.QPushButton, f"mb{i}").setText("")
            self.findTopics_widget.findChild(QtWidgets.QPushButton, f"mb{i}").setEnabled(False)
            self.findTopics_widget.findChild(QtWidgets.QPushButton, f"tb{i}").setText("")
            self.findTopics_widget.findChild(QtWidgets.QPushButton, f"tb{i}").setEnabled(False)



    def get_topic_tweets(self, topic):
        self.clear_table()
        all_topic_tweets = tweet_collator.db_get_tweet_by_topic(topic)
        # get at most 4 tweets randomly
        if len(all_topic_tweets) > 4:
            all_topic_tweets = random.sample(all_topic_tweets, 4)

        for i, tweet in enumerate(all_topic_tweets):
            self.findTopics_widget.findChild(QtWidgets.QLabel, f"tweet{i+1}").setText(tweet[0])
            #check if tweet[2] is NoneType
            if tweet[2] is not None and len(tweet[2]) > 0:
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"mb{i+1}").setText("Media")
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"mb{i+1}").setEnabled(True)
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"mb{i+1}").clicked.connect(lambda state, x=tweet[2] : webbrowser.open(x))
            if tweet[1] is not None and len(tweet[1]) > 0:
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"tb{i+1}").setText("Link")
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"tb{i+1}").setEnabled(True)
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"tb{i+1}").clicked.connect(lambda state, x=tweet[1] : webbrowser.open(x))


    def goto_page(self, widget):
        index = self.stacked_widget.indexOf(widget)
        print(index, widget)
        if index >= 0:
            self.stacked_widget.setCurrentIndex(index)

if __name__ == "__main__":
    qdarktheme.enable_hi_dpi()
    app = QtWidgets.QApplication(sys.argv)
    qdarktheme.setup_theme("auto")
    window = Ui()
    window.show()
    sys.exit(app.exec_())
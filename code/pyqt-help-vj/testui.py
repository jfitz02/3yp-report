import sys
from PyQt5 import QtWidgets, uic, QtGui

from twitter_API import data_collator
from twitter_API.data_collator import filename_creation
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import webbrowser
import os
import re
import random
import sqlite3 as sql

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
    print(os.getcwd())
    # save the wordcloud
    wordcloud.to_file(filename)

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.twitter_tweetset = tweet_collator.get_twitter_tweets()
        self.your_tweetset = tweet_collator.get_tweets()

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
        self.get_toptopics()
        self.get_toptopics(yours=False)

    def get_toptopics(self, yours=True):
        # get tweets
        if yours:
            lbl = "yl"
            prog = "yprog"
            top_topics = tweet_collator.db_get_top_topics(self.your_tweetset)
        else:
            lbl = "tl"
            prog = "tprog"
            top_topics = tweet_collator.db_get_top_topics(self.twitter_tweetset)
            
        # filter to only grab top 5 keys based on value
        top_topics = dict(sorted(top_topics.items(), key=lambda item: item[1], reverse=True)[:5])
        for i, (key, value) in enumerate(top_topics.items()):
            self.topTopics_widget.findChild(QtWidgets.QLabel, f"{lbl}{i+1}").setText(key)
            print(f"value ] {int(value*100)}")
            self.progress = self.topTopics_widget.findChild(QtWidgets.QProgressBar, f"{prog}{i+1}").setValue(int(value*100))
            

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
            print(f"mb{i}")
            self.findTopics_widget.findChild(QtWidgets.QLabel, f"tweet{i}").setText("")
            self.findTopics_widget.findChild(QtWidgets.QPushButton, f"mb{i}").setText("")
            self.findTopics_widget.findChild(QtWidgets.QPushButton, f"mb{i}").setEnabled(False)
            self.findTopics_widget.findChild(QtWidgets.QPushButton, f"tb{i}").setText("")
            self.findTopics_widget.findChild(QtWidgets.QPushButton, f"tb{i}").setEnabled(False)



    def get_topic_tweets(self, topic):
        print("getting topic tweets: ", topic)
        self.clear_table()
        all_topic_tweets = tweet_collator.db_get_tweet_by_topic(topic)
        # get at most 4 tweets randomly
        if len(all_topic_tweets) > 4:
            all_topic_tweets = random.sample(all_topic_tweets, 4)

        for i, tweet in enumerate(all_topic_tweets):
            print(tweet)
            self.findTopics_widget.findChild(QtWidgets.QLabel, f"tweet{i+1}").setText(tweet[0])
            #check if tweet[2] is NoneType
            if tweet[2] is not None and len(tweet[2]) > 0:
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"mb{i+1}").setText("Media")
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"mb{i+1}").setEnabled(True)
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"mb{i+1}").clicked.connect(lambda : webbrowser.open(tweet[2]))
            if tweet[1] is not None and len(tweet[1]) > 0:
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"tb{i+1}").setText("Link")
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"tb{i+1}").setEnabled(True)
                self.findTopics_widget.findChild(QtWidgets.QPushButton, f"tb{i+1}").clicked.connect(lambda : webbrowser.open(tweet[1]))


    def goto_page(self, widget):
        index = self.stacked_widget.indexOf(widget)
        print(index, widget)
        if index >= 0:
            self.stacked_widget.setCurrentIndex(index)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
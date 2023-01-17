import sys
from PyQt5 import QtWidgets, uic, QtGui

from twitter_API import data_collator
from twitter_API import model_api
import os
import re

twitter_processor = model_api.TweetProcessor(os.getcwd(), [])
tweet_collator = data_collator.DataCollator("./twitter_API/pass.secret")

Ui_findTopic, _ = uic.loadUiType("findtopic.ui")
Ui_topTopics, _ = uic.loadUiType("toptopics.ui")
Ui_wordCloud, _ = uic.loadUiType("wordcloud.ui")

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
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

    def get_your_wordcloud(self):
        # get tweets
        tweets = tweet_collator.get_tweets()
        text = ""
        for tweet in tweets:
            text += tweet.full_text + " "

        # remove links, and "RT"
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"RT", "", text)

        twitter_processor.generate_wordcloud(text)

        # get wordcloud.png and load into graphicsView
        self.graphicsView = self.wordCloud_widget.findChild(QtWidgets.QGraphicsView, 'graphicsView')
        self.scene = QtWidgets.QGraphicsScene()

        self.graphicsView.setScene(self.scene)
        
        self.image_qt = QtGui.QImage(f"media_store/wordclouds/{text[-10:]}.png")

        pic = QtWidgets.QGraphicsPixmapItem()
        pic.setPixmap(QtGui.QPixmap.fromImage(self.image_qt))
        self.scene.setSceneRect(0, 0, 335, 370)
        self.scene.addItem(pic)

    def get_twitter_wordcloud(self):
        # get tweets
        tweets = tweet_collator.get_twitter_tweets()
        text = ""
        for tweet in tweets:
            text += tweet.full_text

        # remove links, and "RT"
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"RT", "", text)


        twitter_processor.generate_wordcloud(text)

        # get wordcloud.png and load into graphicsView
        self.graphicsView = self.wordCloud_widget.findChild(QtWidgets.QGraphicsView, 'graphicsView_2')
        self.scene = QtWidgets.QGraphicsScene()

        self.graphicsView.setScene(self.scene)
        
        self.image_qt = QtGui.QImage(f"media_store/wordclouds/{text[-10:]}.png")

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

    def findTopics(self):
        self.findTopics_widget = QtWidgets.QMainWindow()
        Ui_findTopic().setupUi(self.findTopics_widget)
        self.stacked_widget.addWidget(self.findTopics_widget)
        self.button1 = self.findTopics_widget.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button1.clicked.connect(lambda : self.goto_page(self.wordCloud_widget))
        self.button2 = self.findTopics_widget.findChild(QtWidgets.QPushButton, 'pushButton_2')
        self.button2.clicked.connect(lambda : self.goto_page(self.topTopics_widget))

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
import sys
from PyQt5 import QtWidgets, uic, QtGui

from twitter_API import data_collator
from twitter_API import model_api
import os

twitter_processor = model_api.TweetProcessor(os.getcwd(), [])

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

    def get_your_wordcloud(self):
        with open("test.txt", "r") as f:
            text = f.read()

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

# class Ui(QtWidgets.QMainWindow):
#     def __init__(self):
#         super(Ui, self).__init__()
#         self.wordCloud()

#     def wordCloud(self):
#         print("bankApp")
#         self.ui = Ui_wordCloud()
#         self.ui.setupUi(self)
#         self.hide()
#         self.show()
#         self.button = self.findChild(QtWidgets.QPushButton, 'pushButton') 
#         self.button.clicked.connect(self.topTopics)
#         self.button2 = self.findChild(QtWidgets.QPushButton, 'pushButton_2')
#         self.button2.clicked.connect(self.findTopic)


#     def topTopics(self):
#         print("Borrow")
#         self.ui1 = Ui_topTopics()
#         self.ui1.setupUi(self)
#         self.hide()
#         self.show()
#         self.button1 = self.findChild(QtWidgets.QPushButton, 'pushButton') 
#         self.button1.clicked.connect(self.wordCloud)
#         self.button2 = self.findChild(QtWidgets.QPushButton, 'pushButton_2')
#         self.button2.clicked.connect(self.findTopic)


#     def findTopic(self):
#         print("Borrow")
#         self.ui1 = Ui_findTopic()
#         self.ui1.setupUi(self)
#         self.hide()
#         self.show()
#         self.button1 = self.findChild(QtWidgets.QPushButton, 'pushButton') 
#         self.button1.clicked.connect(self.wordCloud)
#         self.button2 = self.findChild(QtWidgets.QPushButton, 'pushButton_2')
#         self.button2.clicked.connect(self.topTopics)


#want to be able to change between above classes via their buttons

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
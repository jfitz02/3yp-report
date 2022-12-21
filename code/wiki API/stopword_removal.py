# read from the csv files and perform stopword removal and stemming
# Path: code\wiki API\read.py
import csv
import nltk
import sys
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

csv.field_size_limit(524288)

stop_words = set(stopwords.words('english'))

def seperate_sentences(text):
    return nltk.sent_tokenize(text)

def remove_whitespace(text):
    return " ".join(text.split())

def preprocess(text):
    text = remove_whitespace(text)
    text = seperate_sentences(text)
    return text

with open("../topics.txt", "r") as f:
    categories = f.read().split("\n")


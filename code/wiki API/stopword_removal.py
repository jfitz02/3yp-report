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
# print(stop_words)

def remove_stopwords(text):
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return filtered_sentence

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))

def remove_numbers(text):
    return ''.join([i for i in text if not i.isdigit()])

def remove_whitespace(text):
    return " ".join(text.split())

def preprocess(text):
    text = remove_punctuation(text)
    text = remove_numbers(text)
    text = remove_whitespace(text)
    text = remove_stopwords(text)
    return text

categories = ["The arts", "Culture", "Entertainment",
                "Games", "Mass media", "Philosophy",
                "Religion", "Science", "Society",
                "Sports", "Technology", "Law",
                "History", "Geography",
                "Esports", "Video games", "Music",
                "Medicine", "Business", "Personal life",
                "Foods", "Disasters", "Nature",
                "Education", "Statistics"]

for category in categories:
    with open(f"./data/{category}.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f,delimiter="\n")
        text = ""
        for row in reader:
            text += row[0]
        text = preprocess(text)
        # print(text)
        with open(f"./data/preprocessed/{category}.csv", "w", encoding="utf-8") as f:
            f.write(" ".join(text))
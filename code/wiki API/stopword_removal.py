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

categories = {"Arts":"The arts", "Culture":"Culture", "Entertainment":"Entertainment",
                "Games":"Games", "MassMedia":"Mass media", "Philosophy":"Philosophy",
                "Religion":"Religion", "Science":"Science", "Society":"Society",
                "Sports":"Sports", "Technology":"Technology", "Law":"Law",
                "History":"History", "Geography":"Geography",
                "Esports":"Esports", "VideoGames":"Video games", "Music":"Music",
                "Medicine":"Medicine", "Business":"Business", "PersonalLife":"Personal life",
                "Foods":"Foods", "Disasters":"Disasters", "Nature":"Nature",
                "Education":"Education", "Statistics":"Statistics"}

for category in categories:
    with open(f"./data/raw/{categories[category]}.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f,delimiter="\n")
        text = ""
        for row in reader:
            text += row[0]
        text = preprocess(text)
        with open(f"./data/preprocessed_BERT/{categories[category]}.csv", "w", encoding="utf-8") as f:
            for sentence in text:
                f.write(f"{category}\t{sentence}")
                f.write("\n")
#imports for re, stopwordsm and word_tokenize
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


#remove punctuation, and non-english words
def remove_punctuation(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]','',text)
    text = re.sub(r'\d+','',text)
    text = re.sub(r'\b\w{1,2}\b','',text)
    text = re.sub(r'\b\w{20,}\b','',text)
    return text

#remove stopwords
def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return ' '.join(filtered_sentence)

def preprocess(sentence):
    sentence = remove_punctuation(sentence)
    sentence = remove_stopwords(sentence)
    return sentence

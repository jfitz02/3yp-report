#import modules for reddit api
import praw
import pandas as pd
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

#get info from pass.secret
with open('pass.secret') as f:
    lines = f.readlines()
    client_id = lines[0].split('=')[1].strip()
    client_secret = lines[1].split('=')[1].strip()
    user_agent = lines[2].split('=')[1].strip()
    username = lines[3].split('=')[1].strip()
    password = lines[4].split('=')[1].strip()

#set up reddit api
reddit = praw.Reddit(client_id=client_id,
                        client_secret=client_secret,
                        user_agent=user_agent,
                        username=username,
                        password=password)

#setup categories for data

print(reddit.user.me())

categories = [
              "Politics", "Economics", "ComputerScience",
              "Mathematics"]

# categories = ["ComputerScience", "MachineLearning"]

#get 1000 most recent posts from each category.
#if there is not 1000 posts, get all posts

for category in categories:
    print(category)
    subreddit = reddit.subreddit(category)
    hot_python = subreddit.hot(limit=1000)
    topics_dict = { "subreddit":[], "body":[]}
    for submission in hot_python:
        topics_dict["subreddit"].append(submission.subreddit)
        topics_dict["body"].append(preprocess(submission.title + " " + submission.selftext.replace("\n", " ")))

    # print(topics_dict)
    topics_data = pd.DataFrame(topics_dict)
    topics_data.to_csv(f"./data/raw/{category}.csv", index=False)


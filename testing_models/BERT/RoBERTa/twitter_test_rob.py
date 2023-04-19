#73%

import pandas as pd
import numpy as np
import sys
import tweepy

sys.path.insert(0, "C:/Users/jfitz/OneDrive/Documents/3rd year project/code/twitter_API")

from twitter_API import data_collator


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


with open("../../../code/topics.txt", "r") as f:
    topics = f.read().splitlines()

print(topics)
api = tweepy.Client("AAAAAAAAAAAAAAAAAAAAAJ77iAEAAAAAss0YBBwoG6uUL4jRZ8Lb33uazJM%3DCHF94D6yWURPdP72kX7XwzrygbKdFX6274Pkz6fVfn5Uk8Ohga",
                    consumer_key="04oihf9AdkyYiwJczU0an9jjc",
                    consumer_secret="XOnAmdRoBNUg2JUTvtmeKIEdxNZjecbdyDkZkeWQ2sw5T16R0v",
                    access_token="750430361964904448-k8qefRA9h52jhTdypdIWAyIBYfkxXWh",
                    access_token_secret="5eMlnQezyMkgIdc1rog5zqQXJfjtFkuQjqTuJce1bZePi")

model = data_collator.TweetProcessor(topics)

tweets = pd.read_csv("../twittertest2.csv", delimiter=",", header=None, names=["label", "tweetid"])

i = 0
# loop through each row in the test data
# compare true value with predicted value
# create confusion matrix

#setup confusion matrix
confusion_matrix = pd.DataFrame(0, index=topics, columns=topics)

for index, row in tweets.iterrows():
    # get tweet
    tweetid = int(row["tweetid"])
    print(tweetid)
    tweet = api.get_tweet(tweetid, tweet_fields=["author_id","conversation_id","in_reply_to_user_id","referenced_tweets"],
                                            expansions=["author_id", "in_reply_to_user_id", "referenced_tweets.id"])
    
    # get conversation of tweet
    conversation = api.search_recent_tweets(f"conversation_id:{tweet.data.conversation_id}",
            tweet_fields=[
                "author_id",
                "created_at"
            ])
    print(conversation)
    # get text of tweet
    text = tweet.data.text

    # get text of all tweets in conversation
    conversation_text = ""
    if conversation.data:
        for tweet in conversation.data:
            conversation_text += tweet.text + " "

    text += " " + conversation_text

    # get true value
    topic = row["label"]

    # get prediction. model.predict returns a list of probabilities for each topic
    prediction = model.predict(text)

    # get index of highest probability
    prediction = np.argmax(prediction)

    # get topic name
    prediction = id2label[prediction]


    # add to confusion matrix
    confusion_matrix.loc[topic, prediction] += 1

#calculate accuracy
accuracy = 0
for i in range(len(topics)):
    accuracy += confusion_matrix.iloc[i,i]

accuracy /= len(tweets)
print(accuracy)

# use seaborn to plot confusion matrix
import seaborn as sn
import matplotlib.pyplot as plt

sn.heatmap(confusion_matrix, annot=True)
plt.tight_layout()
plt.show()


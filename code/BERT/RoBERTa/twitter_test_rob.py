from twitter_API import model_api, data_collator

import pandas as pd
import os

with open("../../topics.txt", "r") as f:
    topics = f.read().splitlines()

print(topics)
dc = data_collator.DataCollator("../../twitter_API/pass.secret")
model = model_api.TweetProcessor(os.getcwd(), topics)

tweets = pd.read_csv("../twittertest.csv", delimiter=",", header=None, names=["label", "tweetid"])

i = 0
# loop through each row in the test data
for index, row in tweets.iterrows():
    if i<56:
        i+=1
        continue
    
    # get tweet
    tweetid = row["tweetid"]
    print(tweetid)
    tweet = dc.get_tweet(tweetid)
    # get media url
    media = dc.find_media_url(tweet)
    print(media)
    if media is None:
        pred = model.get_topic(tweet.full_text)
    elif media[0] == "photo":
        pred = model.get_topic(tweet.full_text, image_url=media[1])
    elif media[0] == "video":
        pred = model.get_topic(tweet.full_text, audio_url=media[1])

    print(f"pred: {pred}.  GT: {row['label']}")

import tweepy
import sqlite3 as sql
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import requests
import librosa
import moviepy.editor as mp
import re

def filename_creation(text, type):
        #remove whitespace
        text = re.sub(r"\W+", "", text)

        #remove special characters
        text = re.sub(r"[^a-zA-Z0-9]+", "", text)
        if type == "wordcloud":
            return f"media_store/wordclouds/{text[-10:]}.png"
        elif type == "video":
            return f"media_store/mp4/{text[-25:-15]}.mp4"
        elif type == "audio":
            return f"media_store/wav/{text[-25:-15]}.wav"
        elif type == "image":
            return f"media_store/jpg/{text[-15:-5]}.jpg"

class TweetProcessor:
    def __init__(self, labels):
        self.labels = labels
        self.topic_tokenizer = AutoTokenizer.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-5")
        self.topic_model = AutoModelForSequenceClassification.from_pretrained("MrFitzmaurice/roberta-finetuned-topic-5")


    def _roberta_call(self, text):
        input_ids = self.topic_tokenizer(text, return_tensors="pt")
        output = self.topic_model(**input_ids)
        pred = output.logits[0].detach().numpy()

        # convert to probabilities
        pred = np.exp(pred) / np.sum(np.exp(pred), axis=0)

        return pred

    def predict(self, text):
        if len(text) > 512:
            text = text[:512]
        pred = self._roberta_call(text)
        return pred


class TestStreaming(tweepy.StreamingClient):
    def __init__(self, bearer_token, twitterfname):
        super().__init__(bearer_token=bearer_token)
        self.received = 0
        self.twitterfname = twitterfname
        with open(self.twitterfname, 'w') as f:
            f.write("")

    def on_connect(self):
        print("Connected to streaming API")

    def on_tweet(self, tweet):
        #remove emojis and new line characters
        tweettext = tweet.text.replace("\n", " ")
        tofile = tweettext + " " + str(tweet.id)+"\n"
        with open(self.twitterfname, 'r', encoding="utf-8") as f:
            exists = (tofile in f.read())

        if not exists:
            with open(self.twitterfname, 'a', encoding="utf-8") as f:
                #write the tweet text, tweet id
                f.write(tofile)

            self.received += 1
            if self.received > 50:
                print("Disconnecting because found tweets")
                self.disconnect()

    def on_disconnect(self):
        print("Disconnected from streaming API")

    def on_error(self, status_code):
        print("Error: {}".format(status_code))

class DataCollator:
    def __init__(self, secrets:str, labels):
        self.labels = labels
        self.tokens = self.get_tokens(secrets)
        self.client = self.get_client()
        streaming_client = TestStreaming(self.tokens["bearer_token"], "tweets.txt")
        streaming_client.filter()

        self.database_connect()
        self.database_setup()

        self.processor = TweetProcessor(labels)

    def database_connect(self):
        self.conn = sql.connect("twitter.db")
        self.c = self.conn.cursor()

    def database_setup(self):
        self.c.execute("""CREATE TABLE IF NOT EXISTS tweetset (
            tweetset_id INTEGER PRIMARY KEY,
            twitter_tweets BOOLEAN,
            medicine_val FLOAT,
            business_val FLOAT,
            videogames_val FLOAT,
            education_val FLOAT,
            religion_val FLOAT,
            science_val FLOAT,
            philosophy_val FLOAT,
            politics_val FLOAT,
            music_val FLOAT,
            sports_val FLOAT,
            law_val FLOAT,
            culture_val FLOAT,
            economics_val FLOAT,
            geography_val FLOAT,
            technology_val FLOAT,
            mathematics_val FLOAT,
            history_val FLOAT,
            foods_val FLOAT,
            disasters_val FLOAT,
            entertainment_val FLOAT
        )""")


        self.c.execute("""CREATE TABLE IF NOT EXISTS tweets (
            tweet_id INTEGER PRIMARY KEY,
            tweetset_id INTEGER,
            tweet_text TEXT,
            tweet_link TEXT,
            tweet_media_link TEXT,
            tweet_topic TEXT,
            FOREIGN KEY (tweetset_id) REFERENCES tweetset (tweetset_id)
        )""")

        self.c.execute("""CREATE TABLE IF NOT EXISTS hashtags (
            hashtag_id INTEGER PRIMARY KEY,
            tweetset_id INTEGER,
            tweet_id INTEGER,
            hashtag TEXT,
            FOREIGN KEY (tweet_id) REFERENCES tweets (tweet_id)
        )""")

        self.conn.commit()

    def get_tokens(self, filename:str):
        token_dict = {}
        with open(filename, 'r') as f:
            for line in f:
                parts = line.split("=")
                token_dict[parts[0].strip()] = parts[1].strip()

        return token_dict

    def get_client(self):
        api = tweepy.API(auth=tweepy.OAuthHandler(self.tokens["consumer_key"],
                                                    self.tokens["consumer_secret"],
                                                    self.tokens["access_token"],
                                                    self.tokens["access_token_secret"]))

        return api

    def get_tweets(self):
        tweets = self.client.home_timeline(tweet_mode="extended", count=50)
        #sum together the prediction vectors for each tweet
        predictions = np.zeros(20)
        tweet_info = []
        for tweet in tweets:
            pred = self.processor.predict(tweet.full_text)
            tweet_info.append((tweet, self.labels[np.argmax(pred)]))
            predictions += pred

        predictions /= len(tweets)

        tweetset_id = self.db_create_tweetset(predictions, False)
        for tweet in tweet_info:
            self.db_create_tweet(tweetset_id, tweet[0], tweet[1])

        return tweetset_id

    def db_create_tweetset(self, preds, twitter_tweets):
        preds = list(preds)
        preds.insert(0, twitter_tweets)
        self.c.execute("INSERT INTO tweetset VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", preds)
        self.conn.commit()
        return self.c.lastrowid

    def db_create_tweet(self, tweetset_id, tweet, topic):
        url = self.find_media_url(tweet)
        if url is not None:
            self.c.execute("INSERT INTO tweets VALUES (NULL, ?, ?, ?, ?, ?)", (tweetset_id, tweet.full_text, "https://twitter.com/twitter/statuses/"+str(tweet.id), url[1], topic))
        else:
            self.c.execute("INSERT INTO tweets VALUES (NULL, ?, ?, ?, ?, ?)", (tweetset_id, tweet.full_text, "https://twitter.com/twitter/statuses/"+str(tweet.id), None, topic))
        
        #find hashtags
        last_tweet_id = self.c.lastrowid
        hashtags = self.find_hashtags(tweet)
        for hashtag in hashtags:
            self.c.execute("INSERT INTO hashtags VALUES (NULL, ?, ?, ?)", (tweetset_id, last_tweet_id, hashtag))
        self.conn.commit()

    def find_hashtags(self, tweet):
        hashtags = []
        for hashtag in tweet.entities["hashtags"]:
            hashtags.append(hashtag["text"])

        return hashtags

    def db_get_hashtags_for_topic(self, tweetset_id, topic):
        self.c.execute("SELECT hashtag FROM hashtags WHERE tweetset_id=? AND tweet_id IN (SELECT tweet_id FROM tweets WHERE tweet_topic=?)", (tweetset_id, topic))
        return self.c.fetchall()

    def db_get_top_topics(self, tweetset_id):
        self.c.execute("SELECT * FROM tweetset WHERE tweetset_id=?", (tweetset_id,))
        # create dict of topic:val
        data = self.c.fetchall()[0]
        topics = {}
        for i in range(len(self.labels)):
            topics[self.labels[i]] = data[i+2]

        return topics

    def db_get_tweets(self, tweetset_id):
        self.c.execute("SELECT tweet_text FROM tweets WHERE tweetset_id=?", (tweetset_id,))
        return self.c.fetchall()

    def db_get_tweet_by_topic(self, topic):
        self.c.execute("SELECT tweet_text, tweet_link, tweet_media_link FROM tweetset INNER JOIN tweets ON tweetset.tweetset_id=tweets.tweetset_id WHERE tweet_topic=? AND tweetset.twitter_tweets=TRUE", (topic,))
        return self.c.fetchall()

    def get_twitter_tweets(self):
        tweets = []
        with open("tweets.txt", 'r', encoding="utf-8") as f:
            for line in f:
                parts = line.split(" ")
                tweet_id = int(parts[-1])
                try:
                    tweets.append(self.get_tweet(tweet_id))
                except tweepy.errors.NotFound:
                    print(f"{tweet_id} not found")
                    pass

        predictions = np.zeros(20)
        tweet_info = []
        for tweet in tweets:
            pred = self.processor.predict(tweet.full_text)
            tweet_info.append((tweet, self.labels[np.argmax(pred)]))
            predictions += pred

        # divide by number of tweets to get average
        predictions /= len(tweets)

        tweetset_id = self.db_create_tweetset(predictions, True)
        for tweet in tweet_info:
            self.db_create_tweet(tweetset_id, tweet[0], tweet[1])

        return tweetset_id

    def get_tweet(self, tweet_id:int):
        tweet = self.client.get_status(tweet_id, tweet_mode="extended")
        return tweet

    def find_media_url(self, tweet):
        media_url = ""
        content_type = ""
        try:
            if not ("media" in tweet.extended_entities):
                return None
        except AttributeError:
            return None
        
        media = tweet.extended_entities["media"][0]
        if media["type"] == "photo":
            content_type = "photo"
            media_url = media["media_url_https"]
        
        elif media["type"] == "video":
            variants = media["video_info"]["variants"]
            for variant in variants:
                if variant["content_type"] == "video/mp4":
                    media_url = variant["url"]
                    content_type = "video"
                    break

        return (content_type, media_url)
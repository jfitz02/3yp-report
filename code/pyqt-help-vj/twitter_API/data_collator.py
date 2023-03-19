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
            if self.received > 100:
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
        self.APIv2 = self.get_APIv2()
        streaming_client = TestStreaming(self.tokens["bearer_token"], "tweets.txt")
        streaming_client.filter()

        self.database_connect()
        self.database_setup()

        self.processor = TweetProcessor(labels)

    def get_APIv2(self):
        return tweepy.Client(self.tokens["bearer_token"], self.tokens["consumer_key"], self.tokens["consumer_secret"], self.tokens["access_token"], self.tokens["access_token_secret"])

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

        self.c.execute("""CREATE TABLE IF NOT EXISTS conversations (
            conversation_id INTEGER PRIMARY KEY,
            topic TEXT,
            tweetset_id INTEGER,
            FOREIGN KEY (tweetset_id) REFERENCES tweetset (tweetset_id)
        )""")


        self.c.execute("""CREATE TABLE IF NOT EXISTS tweets (
            tweet_id INTEGER PRIMARY KEY,
            conversation_id INTEGER,
            tweet_text TEXT,
            tweet_link TEXT,
            tweet_media_link TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
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
        tweetset_id = self.db_create_tweetset(False)
        tweets = self.APIv2.get_home_timeline(tweet_fields=["author_id","conversation_id","in_reply_to_user_id","referenced_tweets","entities"],
                                            expansions=["author_id", "in_reply_to_user_id", "referenced_tweets.id"], max_results=100)
        #sum together the prediction vectors for each tweet
        predictions = np.zeros(20)
        for tweet in tweets[0]:
            convo_id = tweet["conversation_id"]
            self.db_create_conversation(convo_id, tweetset_id)
            self.db_create_tweet(tweetset_id, convo_id, tweet)
            conversation = self.APIv2.search_recent_tweets(query=f"conversation_id:{tweet.id}", tweet_fields="entities")
            text = tweet.text
            if conversation.data is not None and len(conversation.data) > 0:
                for convo in conversation[0]:
                    text += " " + convo.text

            if len(text) > 512:
                text = text[:512]
            pred = self.processor.predict(text)
            self.db_set_conversation_topic(convo_id, self.labels[np.argmax(pred)])
            predictions += pred

        predictions /= len(tweets[0])

        self.db_set_tweetset_scores(tweetset_id, predictions)

        return tweetset_id

    def db_create_tweetset(self, twitter_tweets):
        self.c.execute("INSERT INTO tweetset VALUES (NULL, ?, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)", (twitter_tweets,))
        self.conn.commit()
        return self.c.lastrowid

    def db_set_tweetset_scores(self, tweetset_id, scores):
        self.c.execute("UPDATE tweetset SET medicine_val=?, business_val=?, videogames_val=?, education_val=?, religion_val=?, science_val=?, philosophy_val=?, politics_val=?, music_val=?, sports_val=?, law_val=?, culture_val=?, economics_val=?, geography_val=?, technology_val=?, mathematics_val=?, history_val=?, foods_val=?, disasters_val=?, entertainment_val=? WHERE tweetset_id=?", (scores[0], scores[1], scores[2], scores[3], scores[4], scores[5], scores[6], scores[7], scores[8], scores[9], scores[10], scores[11], scores[12], scores[13], scores[14], scores[15], scores[16], scores[17], scores[18], scores[19], tweetset_id))
        self.conn.commit()

    def db_create_conversation(self, conversation_id, tweetset_id):
        try:
            self.c.execute("INSERT INTO conversations VALUES (?, NULL, ?)", (conversation_id, tweetset_id,))
        except sql.IntegrityError as e:
            print("conversation already exists")
        self.conn.commit()
        return self.c.lastrowid

    def db_set_conversation_topic(self, conversation_id, topic):
        self.c.execute("UPDATE conversations SET topic=? WHERE conversation_id=?", (topic, conversation_id))
        self.conn.commit()

    def db_create_tweet(self, tweetset_id, conversation_id, tweet):
        url = self.find_media_url(tweet)
        if url is not None:
            self.c.execute("INSERT INTO tweets VALUES (NULL, ?, ?, ?, ?)", (conversation_id, tweet.text, "https://twitter.com/twitter/statuses/"+str(tweet.id), url[1]))
        else:
            self.c.execute("INSERT INTO tweets VALUES (NULL, ?, ?, ?, ?)", (conversation_id, tweet.text, "https://twitter.com/twitter/statuses/"+str(tweet.id), None))
        
        #find hashtags
        last_tweet_id = self.c.lastrowid
        hashtags = self.find_hashtags(tweet)
        for hashtag in hashtags:
            self.c.execute("INSERT INTO hashtags VALUES (NULL, ?, ?, ?)", (tweetset_id, last_tweet_id, hashtag))
        self.conn.commit()

    def find_hashtags(self, tweet):
        hashtags = []
        try:
            for hashtag in tweet.entities["hashtags"]:
                hashtags.append(hashtag["tag"])
        except KeyError:
            pass
        except TypeError:
            print("no entities")

        return hashtags

    def db_get_hashtags_for_topic(self, tweetset_id, topic):
        self.c.execute("SELECT hashtag FROM hashtags WHERE tweetset_id=? AND tweet_id IN (SELECT tweet_id FROM tweets INNER JOIN conversations ON tweets.conversation_id=conversations.conversation_id WHERE conversations.topic=?)", (tweetset_id, topic))
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
        # use tweetset to get conversations then get tweets for each conversation
        self.c.execute("SELECT tweets.tweet_text, tweets.tweet_link, tweets.tweet_media_link, conversations.topic FROM tweets INNER JOIN conversations ON tweets.conversation_id=conversations.conversation_id WHERE conversations.tweetset_id=?", (tweetset_id,))
        return self.c.fetchall()

    def db_get_tweet_by_topic(self, topic):
        self.c.execute("SELECT tweet_text, tweet_link, tweet_media_link FROM tweetset INNER JOIN conversations ON tweetset.tweetset_id=conversations.tweetset_id INNER JOIN tweets ON conversations.conversation_id=tweets.conversation_id WHERE conversations.topic=?", (topic,))
        return self.c.fetchall()

    def get_twitter_tweets(self):
        tweets = []
        with open("tweets.txt", 'r', encoding="utf-8") as f:
            for line in f:
                parts = line.split(" ")
                tweet_id = int(parts[-1])
                found_tweet = self.get_tweet(tweet_id)
                if found_tweet.data is not None:
                    tweets.append(self.get_tweet(tweet_id))
                else:
                    print(f"{tweet_id} not found")

        tweetset_id = self.db_create_tweetset(True)

        predictions = np.zeros(20)
        for tweet in tweets:
            if tweet is None:
                print("tweet is none")
                continue
            tweet = tweet[0]
            convo_id = tweet["conversation_id"]
            self.db_create_conversation(convo_id, tweetset_id)
            self.db_create_tweet(tweetset_id, convo_id, tweet)
            conversation = self.APIv2.search_recent_tweets(query=f"conversation_id:{tweet.id}", tweet_fields="entities")
            text = tweet.text
            if conversation.data is not None and len(conversation.data) > 0:
                for convo in conversation[0]:
                    text += " " + convo.text

            if len(text) > 512:
                text = text[:512]
            pred = self.processor.predict(text)
            self.db_set_conversation_topic(convo_id, self.labels[np.argmax(pred)])
            predictions += pred

        # divide by number of tweets to get average
        predictions /= len(tweets)

        # update tweetset with predictions
        self.db_set_tweetset_scores(tweetset_id, predictions)

        return tweetset_id

    def get_tweet(self, tweet_id:int):
        tweet = self.APIv2.get_tweet(tweet_id, tweet_fields=["author_id","conversation_id","in_reply_to_user_id","referenced_tweets","entities"],
                                            expansions=["author_id", "in_reply_to_user_id", "referenced_tweets.id"])
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
# class that acts as a mock api for testing purposes
# we will use the tweet json data in tweets.json
import json
import random

class MockAPI:
    def __init__(self):
        return

    def get_tweet(self, tweet_id, tweet_fields=None, expansions=None):
        tweet_id = str(tweet_id)
        with open("tweets.json", 'r') as f:
            tweets = json.load(f)

        for tweet in tweets:
            if tweet["id"] == tweet_id:
                return {"data":tweet}

        with open("your_tweets.json", 'r') as f:
            your_tweets = json.load(f)

        for tweet in your_tweets:
            if tweet["id"] == tweet_id:
                return {"data":tweet}
        
        return {"data":None}

    def get_tweets(self, tweet_fields=None, expansions=None, count=50):
        #randomly select count number of tweets from tweets.json
        with open("tweets.json", 'r') as f:
            tweets = json.load(f)

        return random.sample(tweets, count)

    def search_recent_tweets(self, query, tweet_fields=None, expansions=None):
        # query is string of form "conversation_id:xxxx"
        #get the conversation id
        convo_id = query.split(":")[1]

        return {"data":self._get_conversation(convo_id)}

    def get_home_timeline(self, tweet_fields=None, expansions=None, max_results=50):
        with open("your_tweets.json", 'r') as f:
            your_tweets = json.load(f)

        return {"data":random.sample(your_tweets, max_results)}

    def _get_conversation(self, convo_id):
        with open("tweets.json", 'r') as f:
            tweets = json.load(f)

        with open("your_tweets.json", 'r') as f:
            your_tweets = json.load(f)

        convo = []
        for tweet in tweets:
            if tweet["conversation_id"] == convo_id:
                convo.append(tweet)

        for tweet in your_tweets:
            if tweet["conversation_id"] == convo_id:
                convo.append(tweet)
                
        return convo


class MockStreamer(MockAPI):
    def __init__(self, bearer_token):
        super().__init__()
        self.connected = True

    def connect(self):
        self.connected = True

    def on_tweet(self, tweet):
        return

    def filter(self):
        tweets = self.get_tweets(count=100)
        for tweet in tweets:
            if not self.connected:
                print("Not connected to stream")
                return
            self.on_tweet(tweet)

    def disconnect(self):
        self.connected = False
# Grab sample of tweets from Twitter API
# Save the json data to a file
import time
import json
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream

# Twitter API credentials
token_dict = {}
with open("../pass.secret", 'r') as f:
    for line in f:
        parts = line.split("=")
        token_dict[parts[0].strip()] = parts[1].strip()

class TestStreaming(tweepy.StreamingClient):
    def __init__(self, bearer_token):
        super().__init__(bearer_token=bearer_token)
        self.received = 0
        self.client = tweepy.Client(bearer_token=token_dict["bearer_token"], consumer_key=token_dict["consumer_key"], consumer_secret=token_dict["consumer_secret"], access_token=token_dict["access_token"], access_token_secret=token_dict["access_token_secret"])

    def on_connect(self):
        print("Connected to streaming API")

    def on_tweet(self, tweet:tweepy.Tweet):
        # convert tweet to json
        tweet_id = tweet.data["id"]
        tweet_info = self.client.get_tweet(tweet_id, tweet_fields=["author_id","conversation_id","in_reply_to_user_id","referenced_tweets","entities"],
                                            expansions=["author_id", "in_reply_to_user_id", "referenced_tweets.id"])

        tweet_json = json.dumps(tweet_info.data.data, indent=4)

        convo_id = tweet_info.data.data["conversation_id"]
        convo_tweets = self.client.search_recent_tweets(query=f"conversation_id:{convo_id}", tweet_fields=["author_id","conversation_id","in_reply_to_user_id","referenced_tweets","entities"],
                                            expansions=["author_id", "in_reply_to_user_id", "referenced_tweets.id"])
        # write json to file
        with open("tweets.json", 'a') as f:
            f.write(tweet_json)
            f.write(",\n")
            try:
                for tweet in convo_tweets.data:
                    f.write(json.dumps(tweet.data, indent=4))
                    f.write(",\n")
            except:
                print("No conversation tweets found")

        self.received += 1
        if self.received >= 300:
            print("Received {} tweets".format(self.received))
            self.disconnect()


    def on_disconnect(self):
        self.received = 0
        print("Disconnected from streaming API")

    def on_error(self, status_code):
        print("Error: {}".format(status_code))


class Timeline:
    def __init__(self):
        self.client = tweepy.Client(bearer_token=token_dict["bearer_token"], consumer_key=token_dict["consumer_key"], consumer_secret=token_dict["consumer_secret"], access_token=token_dict["access_token"], access_token_secret=token_dict["access_token_secret"])

    def get_home_timeline(self, count=50):
        responses = self.client.get_home_timeline(max_results=count, tweet_fields=["author_id","conversation_id","in_reply_to_user_id","referenced_tweets","entities"],
                                            expansions=["author_id", "in_reply_to_user_id", "referenced_tweets.id"])

        for tweet in responses.data:
            #get conversation
            try:
                convo_id = tweet.data["conversation_id"]
                convo_tweets = self.client.search_recent_tweets(query=f"conversation_id:{convo_id}", tweet_fields=["author_id","conversation_id","in_reply_to_user_id","referenced_tweets","entities"],
                                            expansions=["author_id", "in_reply_to_user_id", "referenced_tweets.id"])
            except:
                print("No conversation tweets found")
                continue

            with open("your_tweets.json", 'a') as f:
                f.write(json.dumps(tweet.data, indent=4))
                f.write(",\n")
                if convo_tweets.data:
                    for convo in convo_tweets.data:
                        f.write(json.dumps(convo.data, indent=4))
                        f.write(",\n")
                else:
                    print("No conversation tweets found")

if __name__ == "__main__":
    # create a client
    client = Timeline()

    client.get_home_timeline(count=100)


import tweepy

class DataCollator:
    def __init__(self, filename:str):
        self.tokens = self.get_tokens(filename)
        self.client = self.get_client()

    def get_tokens(self, filename:str):
        token_dict = {}
        with open(filename, 'r') as f:
            for line in f:
                parts = line.split("=")
                token_dict[parts[0].strip()] = parts[1].strip()

        print(token_dict)
        return token_dict

    def get_client(self):
        api = tweepy.API(auth=tweepy.OAuthHandler(self.tokens["consumer_key"],
                                                    self.tokens["consumer_secret"],
                                                    self.tokens["access_token"],
                                                    self.tokens["access_token_secret"]))

        return api

    def get_tweets(self):
        tweets = self.client.home_timeline(tweet_mode="extended")
        return tweets

    def get_tweet(self, tweet_id:int):
        tweet = self.client.get_status(tweet_id, tweet_mode="extended")
        return tweet

    def like_tweet(self, tweet_id:int):
        self.client.like(tweet_id)

    def retweet_tweet(self, tweet_id:int):
        self.client.retweet(tweet_id)

    def like_and_retweet(self, tweet_id:int):
        self.client.like(tweet_id)
        self.client.retweet(tweet_id)
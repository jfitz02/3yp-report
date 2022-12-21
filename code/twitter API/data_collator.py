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
        client = tweepy.Client(
            consumer_key = self.tokens["consumer_key"],
            consumer_secret = self.tokens["consumer_secret"],
            access_token = self.tokens["access_token"],
            access_token_secret = self.tokens["access_token_secret"]
        )
        return client

    def get_tweets(self, count:int):
        tweets = self.client.get_home_timeline(count)
        return tweets

    def like_tweet(self, tweet_id:int):
        self.client.like(tweet_id)

    def retweet_tweet(self, tweet_id:int):
        self.client.retweet(tweet_id)

    def like_and_retweet(self, tweet_id:int):
        self.client.like(tweet_id)
        self.client.retweet(tweet_id)
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
import tweepy

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
    def __init__(self, secrets:str):
        self.tokens = self.get_tokens(secrets)
        self.client = self.get_client()
        streaming_client = TestStreaming(self.tokens["bearer_token"], "tweets.txt")
        streaming_client.filter()

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
        tweets = self.client.home_timeline(tweet_mode="extended", count=50)
        return tweets

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
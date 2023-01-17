import tweepy
from tweepy import StreamRule

#recreate tweets.txt
with open("tweets.txt", 'w') as f:
    f.write("")


token_dict = {}
with open("pass.secret", 'r') as f:
    for line in f:
        parts = line.split("=")
        token_dict[parts[0].strip()] = parts[1].strip()

with open("../../topics.txt", 'r') as f:
    topics = f.read().splitlines()

client = tweepy.Client(consumer_key=token_dict["consumer_key"],
                          consumer_secret=token_dict["consumer_secret"],
                          access_token=token_dict["access_token"],
                          access_token_secret=token_dict["access_token_secret"])

class TestStreaming(tweepy.StreamingClient):
    def __init__(self, bearer_token):
        super().__init__(bearer_token=bearer_token)
        self.received = 0

    def on_connect(self):
        print("Connected to streaming API")

    def on_tweet(self, tweet):
        #remove emojis and new line characters
        tweettext = tweet.text.replace("\n", " ")
        tofile = tweettext + " " + str(tweet.id)+"\n"
        print(tofile)
        with open("tweets.txt", 'r', encoding="utf-8") as f:
            exists = (tofile in f.read())

        if not exists:
            with open("tweets.txt", 'a', encoding="utf-8") as f:
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

streaming_client = TestStreaming(token_dict["bearer_token"])
# streaming_client.filter()

#create new rules that consist of the topics in topics.txt and does not include retweets
# rules = [StreamRule(value=f"{topic} -is:retweet lang:en", tag=topic) for topic in topics]
# #add the rules to the streaming client
# streaming_client.add_rules(rules)

# print(streaming_client.get_rules())

streaming_client.filter()


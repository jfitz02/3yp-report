import tweepy

def get_tokens(filename:str):
    token_dict = {}
    with open(filename, 'r') as f:
        for line in f:
            parts = line.split("=")
            token_dict[parts[0].strip()] = parts[1].strip()

    print(token_dict)
    return token_dict

tokens = get_tokens("pass.secret")

client = tweepy.Client(
    consumer_key = tokens["consumer_key"],
    consumer_secret = tokens["consumer_secret"],
    access_token = tokens["access_token"],
    access_token_secret = tokens["access_token_secret"]
)

# Get the 10 most recent tweets from @twitterapi
tweets = client.get_home_timeline()
for i in range(len(tweets[0])):
    print(tweets[0][i])
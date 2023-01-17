from data_collator import DataCollator

dc = DataCollator("pass.secret")

tweets = dc.get_twitter_tweets()
print(tweets[0].full_text)

mytweets = dc.get_tweets()
print(mytweets[0].full_text)
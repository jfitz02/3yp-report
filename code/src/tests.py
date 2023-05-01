from twitter_API.data_collator import DataCollator
import sqlite3 as sql

id2label = {
    0: "medicine",
    1: "business",
    2: "videogames",
    3: "education",
    4: "religion",
    5: "science",
    6: "philosophy",
    7: "politics",
    8: "music",
    9: "sports",
    10: "law",
    11: "culture",
    12: "economics",
    13: "geography",
    14: "technology",
    15: "mathematics",
    16: "history",
    17: "foods",
    18: "disasters",
    19: "entertainment"
}

def testing_decorator(func):
    def wrapper(*args, **kwargs):
        print("Testing function: {}".format(func.__name__))
        try:
            func(*args, **kwargs)
        except AssertionError:
            print("Test failed!")
            return False
        print("Test passed!")
        return True
    return wrapper

class TestSuite:
    def __init__(self):
        self.dc = DataCollator("./twitter_API/pass.secret", id2label)

    @testing_decorator
    def test_load_tokens(self):
        self.dc.get_tokens("./twitter_API/pass.secret")
        assert self.dc.tokens != None

    @testing_decorator
    def test_get_client(self):
        client = self.dc.get_client()
        client2 = self.dc.get_APIv2()
        assert client != None
        assert client2 != None

    @testing_decorator
    def test_database_creation(self):
        self.dc.database_setup()
        
        conn = sql.connect("twitter.db")
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        assert len(tables) == 4
        assert tables[0][0] == "tweetset"
        assert tables[1][0] == "conversations"
        assert tables[2][0] == "tweets"
        assert tables[3][0] == "hashtags"

        #test the tweetset table structure has 22 columns
        c.execute("PRAGMA table_info(tweetset);")
        columns = c.fetchall()
        assert len(columns) == 22

        #test the conversations table structure has 3 columns
        c.execute("PRAGMA table_info(conversations);")
        columns = c.fetchall()
        assert len(columns) == 3

        #test the tweets table structure has 5 columns
        c.execute("PRAGMA table_info(tweets);")
        columns = c.fetchall()
        assert len(columns) == 5

        #test the hashtags table structure has 4 columns
        c.execute("PRAGMA table_info(hashtags);")
        columns = c.fetchall()
        assert len(columns) == 4

    @testing_decorator
    def test_get_tweets(self):
        tid = self.dc.get_tweets()

        #check database is populated with some tweets
        conn = sql.connect("twitter.db")
        c = conn.cursor()
        c.execute("SELECT * FROM tweets;")
        tweets = c.fetchall()
        assert len(tweets) > 0
         
        #test that tid is an existing tweetsetid
        c.execute("SELECT tweetset_id FROM tweetset;")
        tweetsetids = c.fetchall()
        assert tid in list(map(lambda x: x[0],tweetsetids))

    def run(self):
        passed = True
        passed = passed and self.test_load_tokens()
        passed = passed and self.test_get_client()
        passed = passed and self.test_database_creation()
        passed = passed and self.test_get_tweets()

        if passed:
            print("All tests passed!")
        else:
            print("Some tests failed!")

if __name__ == "__main__":
    ts = TestSuite()
    ts.run()
    
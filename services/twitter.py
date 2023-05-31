import tweepy
from config import Config
import pickle

class Twitter:
    __instance = None
    auth_file = "twitter_auth.pickle"

    @staticmethod 
    def getInstance():
        if Twitter.__instance == None:
            Twitter()
        return Twitter.__instance

    def __init__(self):        
        print("Initializing TwitterAPI object")
        # self.auth = tweepy.OAuthHandler(Config.TWITTER_CONSUMER_KEY, Config.TWITTER_CONSUMER_SECRET, callback = 'oob')
        # self.auth.set_access_token(Config.TWITTER_ACCESS_KEY, Config.TWITTER_ACCESS_TOKEN_SECRET)
        # self.api = tweepy.API(self.auth)
        
        # pin login
        auth = self.load_auth()
        if auth == None: 
            auth = tweepy.OAuthHandler(Config.TWITTER_CONSUMER_KEY, Config.TWITTER_CONSUMER_SECRET, callback = 'oob')
            auth.secure = True
            auth_url = auth.get_authorization_url(signin_with_twitter=True) 
            print(f"Please authorize: {auth_url}")

            verifier = input('PIN: ').strip()
            auth.get_access_token(verifier)
            self.save_auth(auth)

        self.api = tweepy.API(auth)

        if Twitter.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Twitter.__instance = self
    
    def load_auth(self):
        try:
            # Try to load the authorization from the pickle file
            with open(Twitter.auth_file, 'rb') as file:
                auth = pickle.load(file)                
                print("Twitter Authorization loaded from pickle file.")
                return auth
        except FileNotFoundError:
            return None

    def save_auth(self, auth):
        with open(Twitter.auth_file, 'wb') as file:
            pickle.dump(auth, file)
            print("Twitter Authorization saved as pickle file.")

    def get_api(self): 
        return self.api

    def get_tweet(self, tweet_url):
        tweet_id = tweet_url.split("/")[-1]
        tweet = self.api.get_status(tweet_id)        
        return tweet
    
    def get_replies_for_tweet(self, tweet_user, tweet_id):              
        tweets = []
        # for tweet in tweepy.Cursor(self.api.search_tweets, q=f'to:{tweet_user}',lang='en', count=50).items(50):
        #     print(tweet.text)
        #     if hasattr(tweet, 'in_reply_to_status_id'):
        #         if (tweet.in_reply_to_status_id==tweet_id):                    
        #             tweets.append(tweet)
        #             if len(tweets) >= 20:
        #                 break

        return tweets
    
    def reply_to_tweet(self, tweet_id, text):
        return self.api.update_status(status=text, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True) 
        
        
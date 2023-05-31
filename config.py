import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    This class is used to store the bot's configuration.
    You can load it from a .env file.    
    """
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')  
    DISCORD_PREFIX = os.getenv('DISCORD_PREFIX', '!')    
    OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
    TWITTER_ACCESS_KEY = os.getenv('TWITTER_ACCESS_KEY', None)
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', None)

    TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY', None)
    TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET', None)
    TWITTER_AUTO_REPLY = os.getenv('TWITTER_AUTO_REPLY', 'False') == 'True'
    TWITTER_OAUTH_TOKEN = os.getenv('TWITTER_OAUTH_TOKEN', None)
    TWITTER_OAUTH_VERIFIER = os.getenv('TWITTER_OAUTH_VERIFIER', None)
    TWITTER_REPLY_PROMPT = os.getenv("TWITTER_REPLY_PROMPT", None)

    DEBUG = os.getenv('DEBUG', False)

    HELP_TEST_SHORT = "Feature Testing"
    HELP_TEST_LONG = "A command to be changed and experimented with."
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    This class is used to store the bot's configuration.
    You can load it from a .env file.    
    """
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')  
    DISCORD_TOKEN = os.getenv('DISCORD_PREFIX', '!')    
    OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')

    DEBUG = os.getenv('DEBUG', False)

    HELP_TEST_SHORT = "Feature Testing"
    HELP_TEST_LONG = "A command to be changed and experimented with."
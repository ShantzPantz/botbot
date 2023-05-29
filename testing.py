

import json
import re
from config import Config
from services.openai import OpenAIService
from services.twitter import Twitter

class TwitterBot():
    """ A collection of the commands for handling twitter links

            Attributes:
                bot: The instance of the bot that is executing the commands.
    """   

    def __init__(self):
        return

    def is_twitter_link(self, url):
        return url.startswith('https://twitter.com/')
    
    async def reply_to_tweet(self, url, auto_post=False):
        print(f"Twitter link found {url}")
        status = Twitter.getInstance().get_tweet(url) 
        # make sure the tweet isn't from this user, we don't want it replying to it's own tweets.
        if Twitter.getInstance().api.verify_credentials().screen_name == status.user.screen_name:
            print(f"Ignoring Tweet by {status.user.screen_name} because we posted this.")
            return
        
        original_tweet = {
            "user": {
                "name": status.user.name,
                "screen_name": status.user.screen_name,
                "description": status.user.description
            },
            "text": status.text,
            "retweet_count": status.retweet_count
        }

        replies = Twitter.getInstance().get_replies_for_tweet(status.user.screen_name, status.id)
        minified = []
        for r in replies:
            t = {
                "user": {
                    "name": r.user.name,
                    "screen_name": r.user.screen_name,
                    "description": r.user.description
                },
                "text": r.text,
                "retweet_count": r.retweet_count
            }
            minified.append(t)
        
        prompt = f"{json.dumps(original_tweet)}"
        system_prompt = 'You will be presented with data from a tweet. Create a comedic relatable reply to the tweet. You have a dry, self deprecating sense of humour. You are a 40 year old man with 2 kids. Write the tweet in the style of Norm MacDonald. Keep the tweet to under 250 characters. Your hobbies include WW2 Model Airplanes, Pickleball and you are President of the Local Metal Detecting Club.'
        gpt_messages = [
            { "role": "system", "content": system_prompt },
            { "role": "user", "content": prompt }
        ]  

        reply_text = await OpenAIService.getInstance().chat_gpt(gpt_messages) 
        reply_text = reply_text.strip('\"')
        reply_text = re.sub(r'#\S+', '', reply_text) # remove hashtags
        return reply_text
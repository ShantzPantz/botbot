import json
import discord
from discord.ext import commands
from services.twitter import Twitter
from services.openai import OpenAIService
import re
from config import Config

class TwitterBot(commands.Cog):
    """ A collection of the commands for handling twitter links

            Attributes:
                bot: The instance of the bot that is executing the commands.
    """   

    def __init__(self, bot):
        self.bot = bot 

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
        if auto_post:    
            new_tweet = Twitter.getInstance().reply_to_tweet(status.id, reply_text) 
            return new_tweet     
        else: 
            return reply_text
               

    @commands.Cog.listener()
    async def on_message(self, message):
        links = re.findall(r'(https?://[^\s]+)', message.clean_content)
        if len(links) > 0:
            for link in links:
                if self.is_twitter_link(link):
                    channel = discord.utils.get(self.bot.get_all_channels(), name='bot-experiments')
                    try: 
                        new_tweet = await self.reply_to_tweet(link, auto_post=Config.TWITTER_AUTO_REPLY)   
                        if new_tweet != None and hasattr(new_tweet, 'user'):                                             
                            new_url = f"https://twitter.com/{new_tweet.user.screen_name}/status/{new_tweet.id}"                                                    
                            await channel.send(f"I just replied to a tweet: {new_url}")
                        elif not Config.TWITTER_AUTO_REPLY: 
                            await channel.send(f"Auto Reply is off. But I would have tweeted: \n{new_tweet}")
                    except Exception as e:
                        await channel.send(e)
          
async def setup(bot):   
    await bot.add_cog(TwitterBot(bot))  
    me = Twitter.getInstance().api.verify_credentials()
    print(f"Tweeting on behalf of user: {me.screen_name}")
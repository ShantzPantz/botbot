import datetime
import json
from aiohttp import ClientSession
import discord
from discord.ext import commands
from commands.summarybot import ChatlogFormatter
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
    
    async def generate_reply_suggestions(self, tweet, num=3, max_tokens=2500):
        # format the tweet data
        prompt_data = {
            "user": {
                "name": tweet.user.name,
                "screen_name": tweet.user.screen_name,
                "description": tweet.user.description
            },
            "text": tweet.text,
            "retweet_count": tweet.retweet_count
        }
        prompt = json.dumps(prompt_data)
        
        gpt_messages = [
            { "role": "system", "content": Config.TWITTER_REPLY_PROMPT },
            { "role": "user", "content": prompt }
        ]  

        # make openai request
        openai = OpenAIService.getInstance().openai
        openai.aiosession.set(ClientSession())
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=gpt_messages,
            max_tokens=max_tokens,
            top_p=1,
            temperature=1,
            n=num
        )
        await openai.aiosession.get().close()

        return [choice.message.content.strip() for choice in response.choices]
    

    def should_ignore_tweet(self, tweet):
        if Twitter.getInstance().api.verify_credentials().screen_name == tweet.user.screen_name:
            print(f"Ignoring Tweet by {tweet.user.screen_name} because we posted this.")
            return True   
        else:
            return False     
    

    @commands.Cog.listener()
    async def on_message(self, message):               
        links = re.findall(r'(https?://[^\s]+)', message.clean_content)
        if len(links) > 0:
            for link in links:
                if self.is_twitter_link(link):
                    tweet = Twitter.getInstance().get_tweet(link) 
                    if self.should_ignore_tweet(tweet):
                        return

                    channel = discord.utils.get(self.bot.get_all_channels(), name='bot-experiments')
                    try: 
                        await channel.send("Generating some tweet reply suggestions: ")
                        suggestions = await self.generate_reply_suggestions(tweet, 3)
                        for suggestion in suggestions: 
                            await channel.send(f"{tweet.id}:\n{suggestion}")
                       
                    except Exception as e:
                        await channel.send(e)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        try: 
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = self.bot.get_user(payload.user_id)
            if not user:
                user = await self.bot.fetch_user(payload.user_id)

            if message.attachments and len(message.attachments) > 0:
                return 'Ignore this.. This is not a tweet'
            
            if re.match(r'^\d+:\n', message.clean_content):
                message_parts = message.clean_content.split(":\n")
                tweet_id = message_parts[0]
                reply_text = message_parts[1]                
                new_tweet = Twitter.getInstance().reply_to_tweet(tweet_id, reply_text) 
                new_url = f"https://twitter.com/{new_tweet.user.screen_name}/status/{new_tweet.id}"                                                    
                await channel.send(f"I just replied to a tweet: {new_url}")
            
            # check for format of message. 
        except Exception as e:
            await channel.send(e)    

async def setup(bot):      
    await bot.add_cog(TwitterBot(bot))  
    me = Twitter.getInstance().api.verify_credentials()
    print(f"Tweeting on behalf of user: {me.screen_name}")
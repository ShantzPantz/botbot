import re
import discord
from datetime import datetime, timedelta, date
from discord.ext import commands
from discord import app_commands
from discord import BotIntegration
from discord.ext.commands import has_permissions
from utils import strings
from services.openai import OpenAIService  


class ChatlogFormatter():
    def __init__(self, messages):
        self.messages = self.remove_empty(messages)

    def remove_empty(self, messages):
        return [message for message in messages if len(message.clean_content) > 0 and not message.author.bot]

    def as_plaintext(self):
        return "\n".join([f"{m.author.name}: {m.clean_content}" for m in self.messages])
    
    def as_plaintext_chunked(self, num_words=1000):
        chunks = []      
        lines = self.as_plaintext().split("\n")

        for line in lines:
            if len(chunks) == 0 or len(chunks[-1].split(" ")) + len(line.split(" ")) >= num_words:
                chunks.append(line)                                     
            else:               
                chunks[-1] = chunks[-1] + "\n" + line

        return chunks
    

class HistoryHelper():
    def __init__(self, bot):
        self.bot = bot        

    async def get_history(self, channel: discord.TextChannel, start_time: datetime, end_time: datetime = datetime.now()):        
        messages = []
        batch = None
        
        while batch is None or len(batch) == 1000: 
            print(f"Getting batch starting at {start_time}")
            batch = [message async for message in channel.history(limit=1000, after=start_time, before=end_time, oldest_first=True)]
            messages += batch
            print(f"Messages: {len(messages)}")
            start_time = messages[-1].created_at                        

        return messages


class SummaryBot(commands.Cog):
    """ A collection of the commands utilizing openAI for summarizing conversations.

            Attributes:
                bot: The instance of the bot that is executing the commands.
    """

    def __init__(self, bot):
        self.bot = bot  
        self.history = HistoryHelper(bot)     

    @commands.hybrid_command(name='summarize', with_app_command=True, description=strings.HELP_IMG_SHORT, help=strings.HELP_IMG_LONG, aliases=['sum', 'summary'])
    async def _summarize(self, ctx, *, prompt: str):                 
        if ctx.message.channel_mentions:                
            for channel in ctx.message.channel_mentions:                    
                start_time = datetime.today() - timedelta(days=3)
                end_time = datetime.today()
                
                messages = await self.history.get_history(channel, start_time=start_time, end_time=end_time)                           
                logs = ChatlogFormatter(messages).as_plaintext_chunked()
                
                last_summary= ""
                for log in logs:
                    gpt_messages = [
                        {"role": "system", "content": f"You will be provided a discord chat log."},
                        {"role": "user", "content": f"{prompt}\n\n \"{log}\"\n\n {prompt}" }
                    ]
                    print(gpt_messages)
                    try: 
                        last_summary = await OpenAIService.getInstance().chat_gpt(gpt_messages, 1000)
                        
                        index = 0
                        while index < len(last_summary):
                            msg = last_summary[index:index+1900] if len(last_summary[index:]) > 1900 else last_summary[index:]
                            index += 1900
                            await ctx.send(msg)                                
                    except Exception as e: 
                        print(e)
                return
            
    @commands.hybrid_command(name='generate_tweet')
    async def _tweet(self, ctx, channel_name: str):   
        start_date = datetime(2023, 1, 1, 0, 0, 0, 0)
        end_date = datetime.now()
        randomDate = self.bot.random_date(start_date, end_date)
        channel = discord.utils.get(self.bot.get_all_channels(), name=channel_name)      
        await ctx.send(f"Genenerating a tweet from the context of channel #{channel_name} around {randomDate}")        
        start_time = randomDate - timedelta(days=7)
        end_time = randomDate
        
        messages = await self.history.get_history(channel, start_time=start_time, end_time=end_time)                           
        logs = ChatlogFormatter(messages).as_plaintext_chunked()
        
        last_summary= ""
        for log in logs:
            gpt_messages = [
                { "role": "system", "content": 'You will be given a discord chat. Create a comedic relatable tweet using the topics discussed as inspiration. No #hashtags. You have a dry, self deprecating sense of humour. You are a 40 year old man with 2 kids. Do not include names like "mike", "jay", "steve", "brian", "jason", "chris", "yaobviously", "gravyvampire", "softblankies" or "mjb". You can replace those names with words terms like "my friend", "my buddy", "my neighbor", "a guy from work", "my co-worker". Write the tweet in the style of Norm MacDonald. Keep the tweet to under 250 characters. Your hobbies include WW2 Model Airplanes, Pickleball and you are President of the Local Metal Detecting Club.' },
                { "role": "user", "content": log }
            ]
            
            try: 
                last_summary = await OpenAIService.getInstance().chat_gpt(gpt_messages, 2000)
                last_summary = re.sub(r'#\S+', '', last_summary) # remove hashtags
                                         
                index = 0
                while index < len(last_summary):
                    msg = last_summary[index:index+1900] if len(last_summary[index:]) > 1900 else last_summary[index:]
                    index += 1900
                    await ctx.send(msg)                                
            except Exception as e: 
                print(e)
        return


async def setup(bot):   
    await bot.add_cog(SummaryBot(bot))
    
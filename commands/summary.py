import discord
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands
from discord import BotIntegration
from discord.ext.commands import has_permissions
from utils import strings
from services.openai import OpenAIService


class HistoryHelper():
    def __init__(self, bot):
        self.bot = bot

    def chunk_messages(self, messages):
        chunks = []       
        for m in messages:
            line = f"{m.author.name}: {m.clean_content}"
            if len(chunks) == 0 or len(chunks[-1] + line) > 6000:
                chunks.append(line)                                     
            else:               
                chunks[-1] = chunks[-1] + "\n" + line
        
        return chunks

    async def last_day(self, channel: discord.TextChannel):
        start_time = datetime.today() - timedelta(days=1)
        return await self.get_history(channel, start_time)
    
    async def last_days(self, channel: discord.TextChannel, days: int):
        start_time = datetime.today() - timedelta(days=days)
        return await self.get_history(channel, start_time)

    async def get_history(self, channel: discord.TextChannel, start_time: datetime):
        messages = []
        async for message in channel.history(limit=1000, after=start_time, oldest_first=True):
            messages.append(message)

        return messages


class Summary(commands.Cog):
    """ A collection of the commands utilizing openAI for summarizing conversations.

            Attributes:
                bot: The instance of the bot that is executing the commands.
    """

    def __init__(self, bot):
        self.bot = bot  
        self.history = HistoryHelper(bot)     

    @commands.hybrid_command(name='summarize', with_app_command=True, description=strings.HELP_IMG_SHORT, help=strings.HELP_IMG_LONG, aliases=['sum', 'summary'])
    async def _summarize(self, ctx, *, prompt: str):         
        print(prompt)      
        if ctx.message.channel_mentions:
                # Print the IDs of the mentioned channels
                for channel in ctx.message.channel_mentions:
                    messages = await self.history.last_days(channel, 7) 
                    msgs = self.history.chunk_messages(messages)
                    response = OpenAIService.getInstance().summarize_chat(msgs[0], prompt)
                    await ctx.send(f"{channel.name} Messages: {len(messages)}\n\n{response}")
        return
    

async def setup(bot):   
    await bot.add_cog(Summary(bot))    
    
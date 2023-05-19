import re
import traceback
import discord
from discord.ext import commands
from discord import app_commands
from discord import BotIntegration
from discord.ext.commands import has_permissions
from utils import strings
from services.openai import OpenAIService

class General(commands.Cog):
    """ A collection of the commands utilizing openAI.

            Attributes:
                bot: The instance of the bot that is executing the commands.
    """

    def __init__(self, bot):
        self.bot = bot       

    @commands.hybrid_command(name='create', with_app_command=True, description=strings.HELP_IMG_SHORT, help=strings.HELP_IMG_LONG, aliases=['c'])
    async def _create(self, ctx, *, prompt: str):
        try:
            url = OpenAIService.getInstance().create_image(prompt)
            await ctx.send(url)
        except Exception as e:
            await ctx.send(e)


    @commands.hybrid_command(name='edit', with_app_command=True, description=strings.HELP_IMG_SHORT, help=strings.HELP_IMG_LONG, aliases=['e'])
    async def _edit(self, ctx, url: str, *, prompt: str):  
        print(prompt)
        try: 
            modified_url = OpenAIService.getInstance().edit_image(url, prompt)
            await ctx.send(modified_url)
        except Exception as e:
            await ctx.send(e)

    @commands.hybrid_command(name='variant', with_app_command=True, description=strings.HELP_IMG_SHORT, help=strings.HELP_IMG_LONG, aliases=['v'])
    async def _variant(self, ctx, url: str):  
        try:
            modified_url = OpenAIService.getInstance().create_variant(url)
            await ctx.send(modified_url)
        except Exception as e:
            await ctx.send(e)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        try: 
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = self.bot.get_user(payload.user_id)
            if not user:
                user = await self.bot.fetch_user(payload.user_id)

            if message.attachments:
                modified_url = OpenAIService.getInstance().create_variant(message.attachments[0].url)
                await channel.send("Variant: " + modified_url)

            
            links = re.findall(r'(https?://[^\s]+)', message.clean_content)
            if len(links) > 0:
                output = []
                for link in links:
                    modified_url = OpenAIService.getInstance().create_variant(link)
                    output.append(modified_url)
                
                await channel.send("Variant: " + "\n".join(output))
        except Exception as e:
            await channel.send(e)
    

async def setup(bot):   
    await bot.add_cog(General(bot))    
    
    
    

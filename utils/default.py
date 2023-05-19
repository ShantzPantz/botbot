import discord
import os

from discord.ext import commands

class DiscordBot(commands.Bot):
    def __init__(self, config, prefix: list[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix
        self.config = config

    async def setup_hook(self):
        for file in os.listdir("commands"):
            if not file.endswith(".py"):
                continue  # Skip non-python files

            name = file[:-3]
            await self.load_extension(f"commands.{name}")

        # await self.tree.sync(guild = discord.Object(id=356961851679965185))


    async def on_message(self, msg: discord.Message):
        if not self.is_ready() or msg.author.bot:
            return

        await self.process_commands(msg)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=CustomContext)
        await self.invoke(ctx)


class CustomContext(commands.Context):
    """
    This class is used to override discord.py's Context class.
    Any functions added will become usable in ALL commands.    
    """

    def __init__(self, **kwargs):
        self.bot: "DiscordBot"
        super().__init__(**kwargs)
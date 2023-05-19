from typing import Literal, Optional
import discord
from discord.ext.commands import Greedy, Context
from discord.ext import commands
import config
from utils.default import DiscordBot

config = config.Config()
print("Logging in...")

bot = DiscordBot(config=config, command_prefix=config.DISCORD_PREFIX, intents=discord.Intents(
        guilds=True, members=True, messages=True, reactions=True,
        presences=True, message_content=True,
    ))

try: 
    #------ Sync Tree ------
    guild = discord.Object(id=356961851679965185)
    # Get Guild ID from right clicking on server icon
    # Must have devloper mode on discord on setting>Advance>Developer Mode
    #More info on tree can be found on discord.py Git Repo
    @bot.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
    ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @bot.listen()
    async def on_reaction_add(reaction, user):
        print(reaction)

    bot.run(config.DISCORD_TOKEN)
except Exception as e:
    print(f"Error when logging in: {e}")
import discord
from discord.ext import commands, tasks
from discord.utils import get
import os
import psycopg2
import func

intents = discord.Intents.default()
intents.members = True

TOKEN = os.environ["TOKEN"]
DB_NAME= os.environ["DB_NAME"]
DB_USER=os.environ["DB_USER"]
DB_PASS= os.environ["DB_PASS"]
DB_HOST= os.environ["DB_HOST"]
DB_PORT= "5432"

conn = psycopg2.connect(
    database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
)
c = conn.cursor()
c.execute(
    "CREATE TABLE IF NOT EXISTS userdata (userid TEXT, maxHP INT,bal INT, wins INT,losses INT,wprimary TEXT, wsecondary TEXT, potions TEXT)"
)

conn.commit()
conn.close()
print("DB is connected!")


client = commands.Bot(command_prefix="f/", case_insensitive=True)
owner_id = "397648789793669121"
client.remove_command("help")


# loads all the cogs inside the cogs folder on startup
for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and filename != "func.py" and filename != "__init__.py":
        client.load_extension(f"cogs.{filename[:-3]}")


@client.command()
# to load a cog
async def load(ctx, cname):
    author = ctx.message.author.id  # gets the author's id.
    if author == 397648789793669121:  # checks if the authors id matches the owner's id.
        client.load_extension(f"cogs.{cname}")
        await ctx.send(f"Successfully loaded {cname}")
    else:
        await ctx.send("Only the bot owner can use this command.")


@client.command()
# to unload a cog
async def unload(ctx, cname):
    author = ctx.message.author.id  # gets the author's id.
    if author == 397648789793669121:  # checks if the authors id matches the owner's id.
        client.unload_extension(f"cogs.{cname}")
    else:
        await ctx.send("Only the bot owner can use this command!")


@client.command()
# to reaload an ALREADY LOADED cog
async def reload(ctx, cname):
    author = ctx.message.author.id  # gest the author's id.
    if author == 397648789793669121:  # checks if the authors id matches the owner's id.
        client.unload_extension(f"cogs.{cname}")
        client.load_extension(f"cogs.{cname}")
        await ctx.send(f"Successfully reloaded {cname}.")
    else:
        await ctx.send("Only the bot owner can use this command!")


client.run(TOKEN)

import discord
from discord.ext import commands, tasks
import func
from player import Player


class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["balance"])
    async def bal(self, ctx, user: discord.Member = 0):
        if user == 0:
            user = ctx.message.author
        func.entry_check_and_create(user.id)
        Balance = Player(user.id).get_bal()

        embed = discord.Embed(
            colour=discord.Colour.gold(),
            title=f"**{user}'s balance**",
            description=f"You currently have ${Balance}.",
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/693104930717827092/693104965480087672/money_bag.png"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def stats(self, ctx, user: discord.Member = 0):
        if user == 0:
            user = ctx.message.author
        func.entry_check_and_create(user.id)
        player = Player(user.id)
        balance = player.get_bal()
        wins = player.get_wins()
        losses = player.get_loss()
        primary, secondary = player.getLoadout()
        primary = func.itemNameFixer(primary)
        secondary = func.itemNameFixer(secondary)
        potion = func.itemNameFixer(player.get_potion())
        embed = discord.Embed(
            colour=discord.Colour.blue(),
            title=f"{ctx.message.author.name}'s Stats",
            description="The follwing stats are global.",
        )
        embed.set_thumbnail(url=ctx.message.author.avatar_url)
        embed.add_field(name="Balance", value=balance)
        embed.add_field(name="Wins", value=wins)
        embed.add_field(
            name="Losses",
            value=losses,
        )
        embed.add_field(name="Primary", value=primary)
        embed.add_field(name="Secondary", value=secondary)
        embed.add_field(name="Potion",value=potion)
        await ctx.send(embed=embed)

    @commands.command()
    async def support(self, ctx):
        await ctx.send("https://discord.gg/hwcqvKg")


def setup(client):
    client.add_cog(Stats(client))

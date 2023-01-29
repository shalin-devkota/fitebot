import discord
from discord.ext import commands
import asyncio
import psycopg2
import random
import func
import os
from player import Player

TOKEN = os.environ["TOKEN"]
DB_NAME= os.environ["DB_NAME"]
DB_USER=os.environ["DB_USER"]
DB_PASS= os.environ["DB_PASS"]
DB_HOST= os.environ["DB_HOST"]
DB_PORT= "5432"




activeChannels = []
fightMoves= ['primary','secondary','potion']
class Fight (commands.Cog):
    def __init__(self,client):
        self.client = client
        
    
    @commands.command(aliase=['duel','challenge'])  #If you are reading this, good luck. I have given up making it more readabale
    async def fight(self,ctx,enemy:discord.Member):
        if ctx.message.author == enemy: #Checks if someone wants to fight themselves 
            await ctx.send("Love yourself a bit more mate.")  
        elif enemy.bot: #Checks if the mentioned enemyis a bot
            await ctx.send("Not letting you fight my kind. Find someone of your own species.")
        else:
            activePlayer, inactivePlayer = sortPlayers(ctx.message.author,enemy)
            
            func.entry_check_and_create(activePlayer.id) #Creates new entries if someone is using the bot for the first time
            func.entry_check_and_create(inactivePlayer.id)
            channel = ctx.message.channel
           
            if channel in activeChannels:
                await ctx.send("There is already a fight going on in this channel")
                return

            activeChannels.append(channel)
                
            def CheckAccept(message):
                message.content= message.content.lower()
                return message.content=="accept" and message.author == enemy

            await ctx.send(
                f"{enemy.mention}",embed=discord.Embed(colour=discord.Colour.red(),title="Duel invite",description=f"{ctx.message.author.name} has invited you to a duel! Type `accept` in chat to accept!")
                )
            try:
                await self.client.wait_for('message',check=CheckAccept,timeout=30)
                    
                fightMessage = await ctx.send(embed=discord.Embed(colour=discord.Colour.green(),title="Acccepted!",description=" The game will start in 5 seconds. Get ready!"))
                    
                await asyncio.sleep(5)
                await fightMessage.delete()
                    
                while activePlayer.hp > 0 and inactivePlayer.hp > 0:
                    requestMessage=await ctx.send(embed=discord.Embed(colour=discord.Colour.green(),description=f"{activePlayer.mention} make your move! Type in `primary` to use your {activePlayer.get_weapon('primary')}  or `secondary` to use your {activePlayer.get_weapon('secondary')}.If you have one, you can also use your potion by typing in `potion`."))
                        
                    def checkActiveMoves(message):
                        return message.content.lower() in fightMoves and message.author == activePlayer
                    try:
                        fightMove= await self.client.wait_for('message',check=checkActiveMoves,timeout=30)
                        
                        
                        if fightMove.content != "potion":
                            damage, weapon,hitState = getFightMoves(fightMove.content,activePlayer)
                            inactivePlayer.dealDamage(damage)  
                            await ctx.send(embed=discord.Embed(title=f"{hitState}",description=f" {activePlayer.mention} dealt {damage} damage with his {func.itemNameFixer(weapon)}.{inactivePlayer.mention} is left with {inactivePlayer.hp} hp."))  
                        else:
                            
                            hpAdded= activePlayer.apply_potion()
                            activePlayer.heal(hpAdded)
                            if hpAdded > 0:
                                await ctx.send(embed=discord.Embed(colour=discord.Colour.green(),title="Healed",description=f"You used your {activePlayer.get_potion()} and healed for {hpAdded} hp"))
                            else:
                                await ctx.send(embed=discord.Embed(colour=discord.Colour.red(),title="No potion",description=f"You had no potion. You didn't heal and also wasted your turn. GG mate."))
                          
                    except Exception as e:
                        print(e)
                        await ctx.send(embed=discord.Embed(colour=discord.Colour.red(),title="Duel ended",description=f"{activePlayer.mention} failed to make a move in time and lost."))
                        activeChannels.remove(channel)
                        activePlayer.hp = 0 
                        break

                    activePlayer,inactivePlayer = inactivePlayer, activePlayer
                    # Note to self:  Rate limit might be exceded due to the following 2 lines. Look for an alternative if it so happens.
                    await requestMessage.delete()
                    await fightMove.delete()

                winner,loser= winDetector(activePlayer,inactivePlayer)
                await ctx.send(embed=discord.Embed(colour=discord.Colour.green(),title="Victory",description=f"{winner.mention} won with {winner.hp} hp  remaining and earned `50` gold."))
                
                func.statUpdater(winner,50,1,0)
                func.statUpdater(loser,0,0,1)
                activeChannels.remove(channel)
            
            except asyncio.TimeoutError:
                await ctx.send(embed=discord.Embed(colour=discord.Colour.red(),title="Time Out",description=f"{enemy.mention} didn't accept in time."))
                activeChannels.remove(channel)
            

    

    @fight.error
    async def fight_error(self,ctx,error):
        error = getattr(error, "original", error)
        if isinstance(error,commands.MissingRequiredArgument):
            await ctx.send("Who do ya wana fight? Run the command againt but this time mention them.")
    
    @commands.command()
    async def devweapon(self,ctx):
        item = "dweap"
        author=ctx.message.author.id #gets the author's id.
        if author==397648789793669121: #checks if the authors id matches the owner's id.
            conn=psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
            c=conn.cursor()
            c.execute(f"UPDATE userdata SET wprimary='{item}' WHERE userid='{author}'")
            await ctx.send("Added the developer exclusive weapon to your loadout!")
            conn.commit()
            c.close()
            conn.close()
        else:
            await ctx.send("This is a testing feature available only to the developer.")


    

def sortPlayers (author,enemy):
    players = [author,enemy]   #These 4 lines determine the active player (the guy who goes first) 
    turn = random.choices(players)  #and the inactive player (guy who goes second) and create Player objects (check player.py)
    activePlayer = Player(turn [0].id)
    players.remove(turn[0])
    inactivePlayer = Player(players[0].id)
    return activePlayer, inactivePlayer


def getFightMoves(move,player):
    if move.lower() == "primary":
        return player.get_primary()
    elif move.lower() =="secondary":
        return player.get_secondary()
    else:
        return player.apply_potion()
    
def winDetector(active,inactive):
    if active.hp > inactive.hp:
        winner = active
        loser = inactive
    else:
        winner = inactive
        loser = active

    return winner,loser



    





def setup(client):
    client.add_cog(Fight(client))

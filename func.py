import psycopg2
import random
import discord
from discord.ext import commands, tasks
import os
import json


TOKEN = os.environ["TOKEN"]
DB_NAME= os.environ["DB_NAME"]
DB_USER=os.environ["DB_USER"]
DB_PASS= os.environ["DB_PASS"]
DB_HOST= os.environ["DB_HOST"]
DB_PORT= "5432"


activeChannels = []


def itemNameSorter(items):
    items = items.lower()
    items = list(items)
    counter = len(items)
    for i in range(0, counter):
        if items[i] == " ":
            items[i] = "_"

    items = "".join(items)
    print(items)
    return items



def balanceAdjuster(passedid, balance):
    conn = psycopg2.connect(
        database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    c = conn.cursor()
    c.execute(f"UPDATE userdata SET bal={balance} WHERE userid='{passedid}'")
    conn.commit()
    c.close()
    conn.close()


def entry_check_and_create(userid):

    conn = psycopg2.connect(
        database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    c = conn.cursor()
    c.execute(f"SELECT wprimary FROM userdata WHERE userid='{userid}'")
    result = c.fetchone()
    if result is None:
        c.execute(
            f"INSERT INTO userdata (userid,maxHP,bal,wins,losses,wprimary,wsecondary,potions) VALUES('{userid}',100,0,0,0,'wooden_sword','wooden_dagger','0')",
        )
        conn.commit()
    if result is not None:
        pass

    c.close()
    conn.close()







def applyPotionEffect(userID, userHP):
    potionHP = {"small_health_pot": 25, "big_health_pot": 40}
    conn = psycopg2.connect(
        database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    c = conn.cursor()
    c.execute(f"SELECT potions FROM userdata WHERE userid='{userID}'")
    result = c.fetchone()
    availablePotion = result[0]
    c.execute(f"UPDATE userdata SET potions='{0}' WHERE userid='{userID}'")
    conn.commit()
    c.close()
    print(availablePotion)
    userHP += potionHP[f"{availablePotion}"]
    return userHP, availablePotion, potionHP[f"{availablePotion}"]


def statUpdater(player,amount,win,loss):
    currentBalance = player.get_bal()
    currentWins = player.get_wins()
    currentLoss= player.get_loss()

    conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    c = conn.cursor()
    c.execute(f"UPDATE userdata SET bal= {currentBalance + amount},wins ={currentWins+win},losses={currentLoss+loss} WHERE userid='{player.id}'")
    

    conn.commit()
    c.close()
    conn.close()





def itemNameFixer(items):
    items = list(items)
    counter = len(items)
    for i in range(0, counter):
        if items[i] == "_":
            items[i] = " "
    items = "".join(items)
    items = items.title()
    return items


# def isPotionAvailable(userID):
#     print("called")
#     conn = psycopg2.connect(
#         database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
#     )
#     c = conn.cursor()
#     c.execute(f"SELECT potions FROM userdata WHERE userid='{userID}'")
#     result = c.fetchone()
#     availablePotion = result[0]
#     conn.commit()
#     c.close()

#     if availablePotion != str(0):
#         return True
#     else:
#         return False

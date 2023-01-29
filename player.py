import psycopg2
import random
import discord
import func
import os

TOKEN = os.environ["TOKEN"]
DB_NAME= os.environ["DB_NAME"]
DB_USER=os.environ["DB_USER"]
DB_PASS= os.environ["DB_PASS"]
DB_HOST= os.environ["DB_HOST"]
DB_PORT= "5432"

weaponDamages={
    'wooden_sword': random.randint(8,10),
    'light_sword': random.randint(9,12),
    'claymore': random.randint(13,16),
    'dual_sword': random.randint(14,17),
    'heavy_sword': random.randint(15,19),
    'bow': random.randint(18,23),
    'spear': random.randint(23,30),
    'dweap': 100
    
}

weaponHitState= ['Hit','Missed']

hitChance={
    'wooden_sword': 100,
    'light_sword': 95,
    'claymore':90,
    'dual_sword': 85,
    'heavy_sword': 82,
    'bow': 79,
    'spear':75 ,
    'dweap':100
}

secWeaponDamages={
        "wooden_dagger":random.randint(2,4),
        "dagger":random.randint(5,7),
        "khukuri" :random.randint(6,9),
        "throwing_knives":random.randint(9,14),
        "poison_dart":random.randint(12,16)
}



class Player(discord.User):
    def __init__(self,id):
        self.id = id
        self.hp = 100
        
        
    def get_bal(self):
        conn = psycopg2.connect(
            database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        c = conn.cursor()
        c.execute(f"SELECT bal FROM userdata WHERE userid='{self.id}'")
        bal = c.fetchone()

        if bal is None:
            Balance = 0
        if bal is not None:
            balint = int(bal[0])
            Balance = balint
        return Balance
        
     #Not for future : Try to integrate these 3 functions together. 
    
    def get_weapon(self,weapon):  #Easier way to get just the name compared to get_primary / get_secondary
        conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        c = conn.cursor()
        c.execute(f"SELECT w{weapon} FROM userdata WHERE userid='{self.id}'")
        conn.commit
        result = c.fetchone()
        if result is None:
            weapon = "wooden_sword" if weapon == "primary" else "wooden_dagger"
        else:
            weapon = result[0]
        return func.itemNameFixer(weapon)

    def get_primary(self):
        conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        c = conn.cursor()
        c.execute(f"SELECT wprimary FROM userdata WHERE userid='{self.id}'")
        conn.commit
        result = c.fetchone()
        if result is None:
            didItHit = "Hit"
            primaryWeapon = "wooden_sword"
            damage = weaponDamages[primaryWeapon]
        else:
            primaryWeapon = result[0]
            chance = [hitChance[primaryWeapon], 100 - hitChance[primaryWeapon]]
            didItHit = random.choices(weaponHitState, chance)
            if didItHit[0] == "Hit":
                damage = weaponDamages[primaryWeapon]
            else:
                damage = 0
        return damage, primaryWeapon, didItHit[0]

    def get_secondary(self):
        conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        c = conn.cursor()
        c.execute(f"SELECT wsecondary FROM userdata WHERE userid='{self.id}'")
        conn.commit
        result = c.fetchone()

        if result is None:
            secondaryWeapon = "wooden_dagger"
            damage = secWeaponDamages[secondaryWeapon]
        else:
            secondaryWeapon = result[0]
            damage = secWeaponDamages[secondaryWeapon]
            
        state = "Hit"
        return damage,secondaryWeapon,state


    def get_wins(self):
        conn = psycopg2.connect(
            database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        c = conn.cursor()
        c.execute(f"SELECT wins FROM userdata WHERE userid='{self.id}'")
        conn.commit()
        result = c.fetchone()
        if result is None:
            wins = 0
        if result is not None:
            wins = int(result[0])
        c.close()
        conn.close()
        return wins


    def get_loss(self):
        conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        c = conn.cursor()
        c.execute(f"SELECT losses FROM userdata WHERE userid='{self.id}'")
        conn.commit()
        result = c.fetchone()
        if result is None:
            losses = 0
        else:
            losses = int(result[0])
        c.close()
        conn.close()
        return losses


    def getLoadout(self):
        conn = psycopg2.connect(
            database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        c = conn.cursor()
        c.execute(f"SELECT wprimary FROM userdata WHERE userid='{self.id}'")
        result = c.fetchone()
        primary = result[0]

        c.execute(f"SELECT wsecondary FROM userdata WHERE userid='{self.id}'")
        result = c.fetchone()
        secondary = result[0]
        conn.commit()
        c.close()
        return primary, secondary

    def get_potion(self):
        conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        c=conn.cursor()
        c.execute(f"SELECT potions from userdata WHERE userid='{self.id}'")
        result = c.fetchone()
        if result is None:
            return None
        else:
            return result[0]

    def apply_potion(self):
        potionHP = {"small_health_pot": 25, "big_health_pot": 40}
        conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        c = conn.cursor()
        c.execute(f"SELECT potions FROM userdata WHERE userid='{self.id}'")
        result = c.fetchone()
        availablePotion = result[0]
        if availablePotion == '0':
            heal = 0
            
        else: 
            c.execute(f"UPDATE userdata SET potions='{0}' WHERE userid='{self.id}'")
            conn.commit()
            c.close()
            heal = potionHP[f"{availablePotion}"]
            
        return heal       



    def dealDamage(self,damage):
        self.hp -= damage

    def heal(self,heal):
        self.hp += heal

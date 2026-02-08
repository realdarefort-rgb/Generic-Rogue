import os
import random
import time
from pathlib import Path

#region Load Saves
saveFile = Path("savefile.txt")

if not saveFile.exists():
    with open(saveFile, "w") as file:
        pass

with open(saveFile, "r") as file:
    lines = file.readlines()

lines = [line.strip() for line in lines]
bestRound = 0
coins = 0
inventory = []

for line in lines:
    if ":" not in line:
        continue

    key, value = line.split(":", 1)
    value = value.strip()
    if key == "Best Round":
        bestRound = int(value) if value else 0
    elif key == "Coins":
        coins = int(value) if value else 0
    elif key == "Inventory":
        inventory = value.split(",") if value else []

#endregion

#region Game Setup
damage = 0
health = 0

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
clear()

class characterBase:
    def __init__(self, name, health, damage, difficulty):
        self.name = name
        self.health = health
        self.damage = damage
        self.inventory = []
        self.difficulty = difficulty

class playerBase:
    def __init__(self):
        self.name = None
        self.build = None
        self.health = 0
        self.damage = 0

        global coins, inventory
        self.coins = coins
        self.inventory = inventory.copy()

    def setBuild(self, build):
        self.build = build
        if build == "Tank":
            self.health = 100
            self.damage = 8
        elif build == "Brawler":
            self.health = 80
            self.damage = 12

    def applyItem(self, item):
        for stat, value in item["effect"].items():
            if hasattr(self, stat):
                setattr(self, stat, getattr(self, stat) + value)
        if item["name"] not in self.inventory:
            self.inventory.append(item["name"])

player = playerBase()

enemyStats = {
    "Goblin": {"health": 20, "damage": 4},
    "Skeleton": {"health": 15, "damage": 6},
    "Giant": {"health": 50, "damage": 12}
}

def enterUser():
    username = input("""Enter your username:
--> """)
    return username


fastMode = False


def textSpeed():
    while True:
        fastMode = False
        userInput = input("""Text Speed? (fast/slow)
--> """).lower()
        if userInput == "fast":
            fastMode = True
            return fastMode
        elif userInput == "slow":
            fastMode = False
            return fastMode
        else:
            clear()
            continue
        



def sleep(s):
    if not fastMode:
        time.sleep(s)
    if fastMode:
        time.sleep(0.5)

#endregion

#region Shop
shopItems = {
    "1": {"name": "Axe", "price": 200, "effect":{"damage" : 8}},
    "2": {"name": "Double Axe", "price": 2000, "effect":{"damage" : 20}},
}

def buyItem(player, itemID):
    clear()
    item = shopItems[itemID]
    itemName = item["name"]

    if itemName in player.inventory:
        print("You already own this!")
        return

    if player.coins < item["price"]:
        print("Not enough coins!")
        return

    player.coins -= item["price"]
    player.applyItem(item)
    print(f"Bought {itemName}!")

def openShop(player):
    userInput = None
    clear()
    while True:
        print(f"""What do you want to buy?

Coins: {player.coins}

1. Axe (20 damage), 200 coins
2. Double Axe (50 damage), 2000 coins
3. Exit
""")
        userInput = input("--> ")
        if userInput in ("1", "2"):
            buyItem(player, userInput)
        elif userInput == "3":
            clear()
            break
        else:
            clear()
            continue
#endregion

#region Main Menu + Start Game
def chooseBuild():
    clear()
    sleep(0.3)
    while True:
        print("Which build will you pick?\n-Tank\n-Brawler")
        userInput = input("---> ").capitalize()
        if userInput in ("Tank", "Brawler"):
            player.setBuild(userInput)
            clear()
            for itemData in shopItems.values():
                itemName = itemData["name"]
                if itemName in player.inventory:
                    player.applyItem(itemData)
                                  
            sleep(0.5)
            break
        clear()

def mainMenu(player):
    while True:
        userInput = None
        clear()
        print(f"""Welcome to Generic Rogue, {player.name}!

Best Round: {bestRound}
Coins: {player.coins}
Items: {', '.join(player.inventory) if player.inventory else 'None'}

1. Play
2. Shop""")
        
        userInput = input("--> ")
        if userInput == "1":
            chooseBuild()
            break
        elif userInput == "2":
            openShop(player)
        else:
            sleep(0.1)

player.name = enterUser()
fastMode = textSpeed()
sleep(0.5)
print("")
mainMenu(player)
#endregion

#region Fight Functions
def chooseOption():
    print("")
    print("Which option will you pick?")
    userInput = input("""1.Fight   2.Run
--> """)
    return userInput

def attack(self, target):
    sleep(0.3)
    print(f"{self.name} attacks {target.name} for {self.damage} damage!")
    target.health -= self.damage
    sleep(0.75)
    print(f"{target.name} took {self.damage} damage!")
    sleep(0.3)
#endregion

#region Round Logic 
currentRound = 0



spawnRates = {
    "Goblin" : 0.55,
    "Skeleton" : 0.4,
    "Giant" : 0.05
}



def newEnemy():
    enemyNames = list(spawnRates.keys())
    enemyRates = list(spawnRates.values())
    encounterName = random.choices(enemyNames, weights=enemyRates, k=1)[0]
    return encounterName



def roundStart(currentRound):
    roundMultiplier = 1 + (currentRound * 0.05)
    clear()
    sleep(0.2)
    enemyName = newEnemy()
    enemyDetails = enemyStats[enemyName]
    baseHealth = enemyDetails["health"]
    baseDamage = enemyDetails["damage"]
    newHealth = int(baseHealth * roundMultiplier * random.uniform(0.9, 1.1))
    newDamage = int(baseDamage * roundMultiplier * random.uniform(0.9, 1.1))
    difficulty = round(newHealth + newDamage / 50)
    enemyObject = characterBase(enemyName, newHealth, newDamage, difficulty)
    print(f"""You encounter a {enemyObject.name}!
Health: {newHealth}
Damage: {newDamage}""")
    sleep(2)
    return enemyObject



def roundCycle(enemyObject):
    
    while enemyObject.health > 0:
        if player.health <= 0:
            return
        clear()
        print(f"""Round: {currentRound}
Coins: {player.coins}""")
        print(f"{enemyObject.name} Health: {enemyObject.health}")
        print(f"Your Health: {player.health}")
        userInput = chooseOption()
        
        if userInput == "1":
            print("")
            attack(player, enemyObject)
        elif userInput == "2":
            runChance = random.randint(0, 100)
            if runChance > 80:
                print("You ran away successfully!")
                return
            else:
                print("You failed to run!")
        else:
            print("Invalid option! Try again.")
            continue
        if enemyObject.health > 0:
            print("")
            attack(enemyObject, player)
    
    sleep(0.5)
    print("")
    print("You win!")
    wonCoins = enemyObject.difficulty
    player.coins += wonCoins
    print(f"You earnt {wonCoins} coins!")
    sleep(2.5)



while player.health > 0:
    currentRound += 1
    enemyObject = roundStart(currentRound)
    roundCycle(enemyObject)



clear()
print("You lost!")
if currentRound > bestRound:
        bestRound = currentRound
print(f"""
Round: {currentRound}
Best Round: {bestRound}
Coins: {player.coins}
Inventory: {player.inventory}""")



with open(saveFile, "w") as file:
    file.write(f"Best Round: {bestRound}\n")
    file.write(f"Coins: {player.coins}\n")
    file.write(f"Inventory: {','.join(player.inventory)}\n")
#endregion

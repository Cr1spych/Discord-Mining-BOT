import discord
from discord.ext import commands
import random
import asyncio
import json
import os

TOKEN = " "  # Replace with your bot's token

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)

DATA_FILE = "user_data.json"

# Function to load user data from the JSON file
def load_user_data():
    """Загружает данные пользователей из файла."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data():
    """Сохраняет данные пользователей в файл."""
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

def reset_mining_status():
    """Сбрасывает статус майнинга для всех пользователей."""
    for user_id in user_data:
        user_data[user_id]["mining"] = False
    save_user_data()

# Function to get the user's data
user_data = load_user_data()

# Function to reset mining status
reset_mining_status()

# Updated mining devices with more models and balanced prices
mining_devices = {
    "AXIS-X01": {"price": 0, "mining_rate": (1, 3)},   # Lower price and lower mining rate
    "AXIS-X02": {"price": 250, "mining_rate": (2, 4)},   # Mid-range price and mining rate
    "AXIS-X03": {"price": 500, "mining_rate": (3, 6)},   # More mining power for a higher price
    "AXIS-X04": {"price": 1000, "mining_rate": (5, 8)},  # Stronger mining power, more expensive
    "AXIS-X05": {"price": 2500, "mining_rate": (7, 12)}, # Good mining power for higher price
    "AXIS-X06": {"price": 4000, "mining_rate": (9, 15)}, # High-end device with balanced cost
    "AXIS-X07": {"price": 6500, "mining_rate": (12, 18)},# Premium device with a higher mining rate
    "AXIS-X08": {"price": 10000, "mining_rate": (15, 25)}, # Top-tier device with high mining rate
    "AXIS-X09": {"price": 15000, "mining_rate": (18, 30)}, # Elite device, very expensive
}

async def send_dm(ctx, message):
    """Helper function to send a DM to the user."""
    try:
        await ctx.author.send(message)
    except discord.Forbidden:
        await ctx.send("Unable to send a DM. Please check your privacy settings.")

def get_user_data(user_id):
    """Получает или создает запись пользователя."""
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "coins": 0,
            "money": 50,
            "miner": "AXIS-X01",
            "mining": False
        }
        save_user_data()
    return user_data[str(user_id)]

@bot.command(name="me")
async def profile(ctx):
    user = get_user_data(ctx.author.id)
    miner_display = user["miner"] if user["miner"] else "None"
    await send_dm(ctx,
        f"**💳 Your name:** **{ctx.author.name}**\n"
        f"**💸 Your balance:** **{user['money']}$**\n"
        f"**🪙 Your coins:** **{user['coins']}**\n"
        f"**💻 Your mining device:** **{miner_display}**"
    )

@bot.command(name="mine")
async def mine(ctx):
    user = get_user_data(ctx.author.id)
    
    # Check if the user is already mining
    if user["mining"]:
        await send_dm(ctx, "**⛔ You are already mining!**")
        return
    
    # Check if the user has a mining tool
    if not user["miner"]:
        await send_dm(ctx, "**❌ You don't have a mining tool! Buy one using the `.shop` command.**")
        return

    # Start mining
    user["mining"] = True
    save_user_data()  # Save mining state
    
    await send_dm(ctx, "**💎 Mining has started! It will take 10 seconds...**")
    
    # Simulate mining process
    await asyncio.sleep(10)

    # Calculate mined coins based on the mining tool's rate
    mining_rate = mining_devices[user["miner"]]["mining_rate"]
    mined_coins = random.randint(mining_rate[0], mining_rate[1])

    # Update user data
    user["coins"] += mined_coins
    user["mining"] = False
    save_user_data()

    # Inform the user of the mining results
    await send_dm(ctx, f"**✅ Mining completed! You mined {mined_coins}🪙. Your new coin balance: {user['coins']}🪙**")

@bot.command(name="buy")
async def buy(ctx, miner_name):
    user = get_user_data(ctx.author.id)
    
    # Check if the specified miner exists
    if miner_name not in mining_devices:
        await send_dm(ctx, "**❌ Such a mining device does not exist!**")
        return
    
    # Get the current miner data and the new miner data
    current_miner = user["miner"]
    new_miner = mining_devices[miner_name]
    
    # Compare the power of the current miner and the new miner
    current_miner_price = mining_devices[current_miner]["price"]
    new_miner_price = new_miner["price"]

    # If the user already has a better or equal miner
    if current_miner_price > new_miner_price:
        await send_dm(ctx, f"**❌ You already own a better or equally powerful miner ({current_miner}). You can't buy {miner_name} now.**")
        return

    # If the user doesn't have enough money to buy the new miner
    if new_miner_price > user["money"]:
        await send_dm(ctx, f"**❌ You don't have enough money to buy {miner_name}. Cost: {new_miner_price}$**")
        return
    
    # Proceed with the purchase
    user["miner"] = miner_name
    user["money"] -= new_miner_price
    save_user_data()
    
    await send_dm(ctx, f"**✅ You successfully bought {miner_name} for {new_miner_price}$! Your new balance: {user['money']}$**")

@bot.command(name="exchange")
async def sell(ctx, amount: int):
    user = get_user_data(ctx.author.id)
    exchange_rate = random.randint(5, 20)
    if amount <= 0:
        await send_dm(ctx, "**❌ You cannot sell a negative amount of coins!**")
        return
    if amount > user["coins"]:
        await send_dm(ctx, f"**❌ You don't have enough coins! Your current balance: {user['coins']}🪙**")
        return
    user["coins"] -= amount
    profit = amount * exchange_rate
    user["money"] += profit
    save_user_data()
    await send_dm(ctx,
        f"**✅ You successfully sold {amount}🪙 for {profit}$ (rate: 1 coin = {exchange_rate}$).**\n"
        f"**Your new balance: {user['money']}$, coins: {user['coins']}🪙**"
    )

@bot.command(name="shop")
async def shop(ctx):
    await send_dm(ctx, "**🛒 Mining Device Shop:**\n"
                        "**1. AXIS-X01 - Free — Mine 1-3 coins.**\n"
                        "**2. AXIS-X02 - 250$ — Mine 2-4 coins.**\n"
                        "**3. AXIS-X03 - 500$ — Mine 3-6 coins.**\n"
                        "**4. AXIS-X04 - 1000$ — Mine 5-8 coins.**\n"
                        "**5. AXIS-X05 - 2500$ — Mine 7-12 coins.**\n"
                        "**6. AXIS-X06 - 4000$ — Mine 9-15 coins.**\n"
                        "**7. AXIS-X07 - 6500$ — Mine 12-18 coins.**\n"
                        "**8. AXIS-X08 - 10000$ — Mine 15-25 coins.**\n"
                        "**9. AXIS-X09 - 15000$ — Mine 18-30 coins.**\n\n"
                        "**To buy a mining device, use the `.buy <device name>` command.**")

@bot.command(name="roulette")
async def roulette(ctx, bet_amount: int):
    user = get_user_data(ctx.author.id)
    
    # Check if the user has enough coins for the bet
    if bet_amount <= 0:
        await send_dm(ctx, "**❌ You cannot bet a negative amount or zero coins!**")
        return
    
    if bet_amount > user["coins"]:
        await send_dm(ctx, f"**❌ You don't have enough coins! Your current balance: {user['coins']}🪙**")
        return
    
    # Possible outcomes: 'win' or 'lose'
    outcomes = ['win', 'lose']
    result = random.choice(outcomes)  # Randomly choose between 'win' and 'lose'

    if result == 'win':
        # User wins: They get double their bet amount
        winnings = bet_amount * 2
        user["coins"] += winnings
        save_user_data()
        await send_dm(ctx, f"**🎉 You won the roulette! You earned {winnings}🪙. Your new coin balance: {user['coins']}🪙**")
    else:
        # User loses: They lose their bet
        user["coins"] -= bet_amount
        save_user_data()
        await send_dm(ctx, f"**❌ You lost in roulette. You lost {bet_amount}🪙. Your new coin balance: {user['coins']}🪙**")

bot.run(TOKEN)

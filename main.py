import discord
from discord.ext import commands
import random
import asyncio
import json
import os

TOKEN = (" ")  # Your token here

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)

DATA_FILE = "user_data.json"

# Function to load user data from the JSON file
def load_user_data():
    """Loads user data from the file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data():
    """Saves user data to the file."""
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

def reset_mining_status():
    """Resets mining status for all users."""
    for user_id in user_data:
        user_data[user_id]["mining"] = False
    save_user_data()

# Function to get the user's data
user_data = load_user_data()

# Function to reset mining status
reset_mining_status()

videocards = {
    "GTX550": {"price": 0, "mining_rate": (1, 2)},
    "GTX1080": {"price": 50, "mining_rate": (1, 3)},
    "GTX1650": {"price": 250, "mining_rate": (2, 5)},  # Adjusted for better balance
    "RTX2060": {"price": 450, "mining_rate": (3, 7)},  # Adjusted
    "RTX3060": {"price": 800, "mining_rate": (4, 9)},  # Adjusted
    "RTX4090": {"price": 1500, "mining_rate": (6, 12)}, # Adjusted
    "RTX5080": {"price": 3000, "mining_rate": (8, 15)}, # Adjusted
    "RTX6100": {"price": 6000, "mining_rate": (10, 20)}, # Adjusted
}

async def send_dm(ctx, message):
    """Helper function to send a DM to the user."""
    try:
        await ctx.author.send(message)
    except discord.Forbidden:
        await ctx.send("Unable to send a DM. Please check your privacy settings.")

def get_user_data(user_id):
    """Gets or creates a user record."""
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "coins": 0,
            "money": 50,
            "videocard": "GTX550",
            "mining": False
        }
        save_user_data()
    return user_data[str(user_id)]

@bot.command(name="me")
async def profile(ctx):
    user = get_user_data(ctx.author.id)
    videocard_display = user["videocard"] if user["videocard"] else "None"
    await send_dm(ctx,
        f"**💳 Your name:** **{ctx.author.name}**\n"
        f"**💸 Your balance:** **${user['money']}**\n"
        f"**🪙 Your coins:** **{user['coins']}**\n"
        f"**📺 Graphics card:** **{videocard_display}**"
    )

@bot.command(name="mine")
async def mine(ctx):
    user = get_user_data(ctx.author.id)
    if user["mining"]:
        await send_dm(ctx, "**⛔ You are already mining!**")
        return
    if not user["videocard"]:
        await send_dm(ctx, "**❌ You don't have a graphics card for mining! Buy one using the `.shop` command.**")
        return
    user["mining"] = True
    save_user_data()
    await send_dm(ctx, "**💎 You started mining! This will take 10 seconds.**")
    await asyncio.sleep(10)
    user["mining"] = False
    mined_coins = random.randint(videocards[user["videocard"]]["mining_rate"][0], videocards[user["videocard"]]["mining_rate"][1])
    user["coins"] += mined_coins
    save_user_data()
    await send_dm(ctx, f"**✅ Mining finished! You earned {mined_coins}🪙. Your new coin balance: {user['coins']}🪙**")

@bot.command(name="buy")
async def buy(ctx, videocard_name):
    user = get_user_data(ctx.author.id)
    if videocard_name not in videocards:
        await send_dm(ctx, "**❌ This graphics card is not available!**")
        return
    if videocards[videocard_name]["price"] > user["money"]:
        await send_dm(ctx,
            f"**❌ You don't have enough dollars to buy {videocard_name}. "
            f"Price: {videocards[videocard_name]['price']}$**"
        )
        return
    user["videocard"] = videocard_name
    user["money"] -= videocards[videocard_name]["price"]
    save_user_data()
    await send_dm(ctx,
        f"**✅ You successfully bought {videocard_name} for {videocards[videocard_name]['price']}$."
        f" Your new balance: {user['money']}$**"
    )

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
    await send_dm(ctx, "**🛒 Shop for graphics cards:**\n**1. GTX1080 - 50$ — Farm 1 - 3 coins.**\n**2. GTX1650 - 250$ — Farm 2 - 5 coins.**\n**3. RTX2060 - 450$ — Farm 3 - 7 coins.**\n**4. RTX3060 - 800$ — Farm 4 - 9 coins.**\n**5. RTX4090 - 1500$ — Farm 6 - 12 coins.**\n**6. RTX5080 - 3000$ — Farm 8 - 15 coins.**\n**7. RTX6100 - 6000$ — Farm 10 - 20 coins.**\n\n**To buy a graphics card, use the command `.buy <videocard name>`.**")

# Roulette game
@bot.command(name="roulette")
async def roulette(ctx, bet: int):
    user = get_user_data(ctx.author.id)
    
    # Check if the player has enough money to place a bet
    if bet <= 0:
        await send_dm(ctx, "**❌ You can't bet zero or negative coins!**")
        return
    if bet > user["coins"]:
        await send_dm(ctx, f"**❌ You don't have enough coins! Your current balance: {user['coins']}🪙**")
        return
    
    # Roll the roulette
    roll = random.randint(0, 36)  # 0 to 36 for a typical roulette wheel
    win = random.choice([True, False])  # Random win/lose outcome

    if win:
        # Double the bet if the user wins
        user["coins"] += bet
        result_message = f"**🎉 You won! You bet {bet}🪙 and won {bet}🪙. Your new balance: {user['coins']}**🪙"
    else:
        # Deduct the bet if the user loses
        user["coins"] -= bet
        result_message = f"**💔 You lost! You bet {bet}🪙 and lost. Your new balance: {user['coins']}**🪙"

    save_user_data()
    await send_dm(ctx, result_message)

bot.run(TOKEN)

# .me - Displays the user's profile (coins, money, graphics card)
# .mine - Starts mining and earns coins based on the user's graphics card
# .buy <videocard_name> - Allows the user to buy a new graphics card
# .exchange <amount> - Sells a specified amount of coins for money
# .shop - Displays a list of available graphics cards for purchase
# .roulette <bet_amount> - Plays roulette, allowing the user to bet coins and potentially win or lose

             

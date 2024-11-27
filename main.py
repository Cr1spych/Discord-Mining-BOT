import discord
from discord.ext import commands
import random
import asyncio
import json
import os

TOKEN = (" ") #Your token here

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

videocards = {
    "GTX550": {"price": 0, "mining_rate": (1, 2)},
    "GTX1080": {"price": 50, "mining_rate": (1, 3)},
    "GTX1650": {"price": 300, "mining_rate": (1, 4)},
    "RTX2060": {"price": 500, "mining_rate": (1, 6)},
    "RTX3060": {"price": 1000, "mining_rate": (1, 9)},
}

async def send_dm(ctx, message):
    """Helper function to send a DM to the user."""
    try:
        await ctx.author.send(message)
    except discord.Forbidden:
        await ctx.send("Не удалось отправить сообщение в ЛС. Проверьте настройки конфиденциальности.")

def get_user_data(user_id):
    """Получает или создает запись пользователя."""
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
    videocard_display = user["videocard"] if user["videocard"] else "Нет"
    await send_dm(ctx,
        f"**💳 Ваше имя:** **{ctx.author.name}**\n"
        f"**💸 Ваш баланс:** **{user['money']}$**\n"
        f"**🪙 Ваши коины:** **{user['coins']}**\n"
        f"**📺 Видеокарта:** **{videocard_display}**"
    )

@bot.command(name="mine")
async def mine(ctx):
    user = get_user_data(ctx.author.id)
    if user["mining"]:
        await send_dm(ctx, "**⛔ Вы уже начали майнинг!**")
        return
    if not user["videocard"]:
        await send_dm(ctx, "**❌ У вас нет видеокарты для майнинга! Купите её с помощью команды `.shop`.**")
        return
    user["mining"] = True
    save_user_data()
    await send_dm(ctx, "**💎 Вы начали майнинг! Это займет 10 секунд.**")
    await asyncio.sleep(10)
    user["mining"] = False
    mined_coins = random.randint(videocards[user["videocard"]]["mining_rate"][0], videocards[user["videocard"]]["mining_rate"][1])
    user["coins"] += mined_coins
    save_user_data()
    await send_dm(ctx, f"**✅ Майнинг завершён! Вы получили {mined_coins}🪙. Ваш новый баланс коинов: {user['coins']}🪙**")

@bot.command(name="buy")
async def buy(ctx, videocard_name):
    user = get_user_data(ctx.author.id)
    if videocard_name not in videocards:
        await send_dm(ctx, "**❌ Такой видеокарты нет!**")
        return
    if videocards[videocard_name]["price"] > user["money"]:
        await send_dm(ctx,
            f"**❌ У вас недостаточно долларов для покупки {videocard_name}. "
            f"Стоимость: {videocards[videocard_name]['price']}$**"
        )
        return
    user["videocard"] = videocard_name
    user["money"] -= videocards[videocard_name]["price"]
    save_user_data()
    await send_dm(ctx,
        f"**✅ Вы успешно купили {videocard_name} за {videocards[videocard_name]['price']}$. "
        f"Ваш новый баланс: {user['money']}$**"
    )

@bot.command(name="exchange")
async def sell(ctx, amount: int):
    user = get_user_data(ctx.author.id)
    exchange_rate = random.randint(5, 20)
    if amount <= 0:
        await send_dm(ctx, "**❌ Вы не можете продать отрицательное количество коинов!**")
        return
    if amount > user["coins"]:
        await send_dm(ctx, f"**❌ У вас недостаточно коинов! Ваш текущий баланс: {user['coins']}🪙**")
        return
    user["coins"] -= amount
    profit = amount * exchange_rate
    user["money"] += profit
    save_user_data()
    await send_dm(ctx,
        f"**✅ Вы успешно продали {amount}🪙 за {profit}$ (курс: 1 коин = {exchange_rate}$).**\n"
        f"**Ваш новый баланс: {user['money']}$, коины: {user['coins']}🪙**"
    )

@bot.command(name="shop")
async def shop(ctx):
    await send_dm(ctx, "**🛒 Магазин видеокарт:**\n**1. GTX1080 - 50$ — Фарм 1 - 2 коинов.**\n**2. GTX1650 - 300$ — Фарм 1 - 3 коинов.**\n**3. RTX2060 - 500$ — фарм 1 - 5 коинов.**\n**4. RTX3060 - 1000$ — фарм 1 - 8 коинов.**\n \n**Чтобы купить видеокарту, используйте команду `.buy <название видеокарты>`.**")

bot.run(TOKEN)

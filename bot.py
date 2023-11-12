import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, time, timedelta
from pytz import timezone
from dotenv import load_dotenv

from tips_scraper import TipsScraper

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix=lambda message: None, intents=intents)

last_tip_message = None  # Variable to store the last sent tip message

scraper = TipsScraper()

async def create_tip_message():
    match, bet, quote, date, units = await scraper.scrape_for_tips()
    tip_message = (
        f"🚨 **TIP OF THE DAY {date}** 🚨\n"
        f"**Match:** {match}\n"
        f"**Bet:** {bet}\n"
        f"**Quote:** {quote}\n"
        f"**Betting Units:** {units}"
    )
    return tip_message

@bot.tree.command(name='sendtip', description="Send the daily tip")
@app_commands.checks.has_permissions(administrator=True)
async def send_tip(interaction: discord.Interaction):
    try:
        global last_tip_message
        new_tip_message = await create_tip_message()

        await interaction.response.send_message(new_tip_message)
        last_tip_message = new_tip_message
    except Exception as e:
        print(f"Error in send_tip command: {e}")


async def send_daily_tip():
    global last_tip_message
    await bot.wait_until_ready()
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel is None:
        print("Channel not found.")
        return

    while not bot.is_closed():
        now = datetime.now(timezone('Europe/Berlin'))
        target_time = timezone('Europe/Berlin').localize(datetime.combine(now.date(), time(0, 0)))
        if now.time() > target_time.time():
            target_time += timedelta(days=1)  # Move to the next day

        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        new_tip_message = await create_tip_message()

        if new_tip_message == last_tip_message:
            print("Similar tip detected, scheduling new scrape in 8 hours.")
            await asyncio.sleep(28800)
            new_tip_message = await create_tip_message()

        await channel.send(new_tip_message)  # Sending message to the channel
        last_tip_message = new_tip_message

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as exception:
        print(exception)

    for guild in bot.guilds:
        print(f"Guild ID: {guild.id} (Name: {guild.name})")
    bot.loop.create_task(send_daily_tip())

bot.run(TOKEN)
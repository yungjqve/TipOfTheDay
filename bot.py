import os
import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
import asyncio
from datetime import datetime, time, timedelta
from pytz import timezone
from dotenv import load_dotenv

from commands.results_command import create_results_embed, league_ids
from commands.sendtip_command import send_tip, create_tip_message

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix=lambda message: None, intents=intents)

@bot.tree.command(name='sendtip', description="Send the daily tip")
@app_commands.checks.has_permissions(administrator=True)
async def send_tip_wrapper(interaction: discord.Interaction):
    await send_tip(interaction)

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

@bot.tree.command(name='results', description="Get football match results")
@app_commands.describe(matchday='Enter the matchday number to get results', 
                       league='Choose the league')
@app_commands.choices(league=[app_commands.Choice(name=name, value=name) for name in league_ids.keys()])
async def results(interaction: discord.Interaction, matchday: int, league: str):
    embed_or_message = create_results_embed(league, matchday)
    
    if isinstance(embed_or_message, Embed):
        await interaction.response.send_message(embed=embed_or_message)
    else:
        await interaction.response.send_message(embed_or_message, ephemeral=True)

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
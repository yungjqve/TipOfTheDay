import os
import discord
from discord.ext import commands
from discord import app_commands
from discord import Embed
from discord.ui import Button, View
from pytz import timezone
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from commands.results_command import create_results_embed, league_ids
from commands.sendtip_command import send_tip, create_tip_message, get_further_tips

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

    # Create a button and view as before
    button = Button(label="View Further Tips", style=discord.ButtonStyle.primary, custom_id="view_further_tips")
    view = View()
    view.add_item(button)

    # Edit the original response to add the button
    await interaction.edit_original_response(view=view)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get('custom_id')

        if custom_id == "view_further_tips":
            tips = await get_further_tips()
            # Format the message to align the tips and risks in a table-like structure
            tips_message = "```"
            for i in range(0, len(tips), 2):
                tips_message += f"{tips[i]:<30} | {tips[i+1]}\n"
            tips_message += "```"
            await interaction.response.send_message(tips_message, ephemeral=True)

scheduler = AsyncIOScheduler()

async def scheduled_task():
    channel = bot.get_channel(int(CHANNEL_ID))
    new_tip_message = await create_tip_message()
    await channel.send(new_tip_message)

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
    
    scheduler.add_job(scheduled_task, CronTrigger(hour=17, minute=2, timezone=pytz.timezone("Europe/Berlin")))
    scheduler.start()


bot.run(TOKEN)
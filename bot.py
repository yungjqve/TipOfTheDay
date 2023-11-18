import os
import discord
from discord.ext import commands
from discord import app_commands, Embed
from discord.ui import Button, View
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging

from commands.results_command import create_results_embed, league_ids
from commands.sendtip_command import send_tip, create_tip_message, get_further_tips
from commands.tips_command import create_tips_embed, league_ids_tips

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Global Error Handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(f"An error occurred: {error}")

@bot.tree.command(name='sendtip', description="Send the daily tip")
@app_commands.checks.has_permissions(administrator=True)
async def send_tip_wrapper(interaction: discord.Interaction):
    try:
        await send_tip(interaction)

        button = Button(label="View Further Tips", style=discord.ButtonStyle.primary, custom_id="view_further_tips")
        view = View()
        view.add_item(button)

        await interaction.edit_original_response(view=view)
    except Exception as e:
        logging.error(f"Error in send_tip_wrapper: {e}")
        await interaction.response.send_message("An error occurred while sending the tip.", ephemeral=True)

# Specific Command Error Handler
@send_tip_wrapper.error
async def send_tip_wrapper_error(interaction, error):
    if isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get('custom_id')

        if custom_id == "view_further_tips":
            try:
                tips = await get_further_tips()
                tips_message = "```"
                for i in range(0, len(tips), 2):
                    tips_message += f"{tips[i]:<30} | {tips[i+1]}\n"
                tips_message += "```"
                await interaction.response.send_message(tips_message, ephemeral=True)
            except Exception as e:
                logging.error(f"Error in on_interaction: {e}")
                await interaction.response.send_message("An error occurred while retrieving further tips.", ephemeral=True)

scheduler = AsyncIOScheduler()

async def scheduled_task():
    try:
        channel = bot.get_channel(int(CHANNEL_ID))
        new_tip_message = await create_tip_message()

        button = Button(label="View Further Tips", style=discord.ButtonStyle.primary, custom_id="view_further_tips")
        view = View()
        view.add_item(button)

        await channel.send(new_tip_message, view=view)
    except Exception as e:
        await channel.send("Today, there is no Tip Of The Day 😭")
        logging.error(f"Error during scheduled task: {e}")

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

@bot.tree.command(name='tips', description="Get football match tips")
@app_commands.describe(league='Choose the league')
@app_commands.choices(league=[app_commands.Choice(name=name, value=name) for name in league_ids_tips.keys()])
async def tips(interaction: discord.Interaction, league: str):
    await interaction.response.defer()
    embed_or_message = await create_tips_embed(league)

    if isinstance(embed_or_message, Embed):
        await interaction.followup.send(embed=embed_or_message)
    else:
        await interaction.followup.send(embed_or_message, ephemeral=True)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(f"Error in on_ready: {e}")

    for guild in bot.guilds:
        print(f"Guild ID: {guild.id} (Name: {guild.name})")
    
    scheduler.add_job(scheduled_task, CronTrigger(hour=8, minute=0, timezone=pytz.timezone("Europe/Berlin")))
    scheduler.start()

bot.run(TOKEN)
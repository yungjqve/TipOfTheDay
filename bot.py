import os
import discord
from dotenv import load_dotenv
# Import the required variables from scrape.py
from scrape import match, bet, quote

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    for guild in client.guilds:
        print(f"Guild ID: {guild.id} (Name: {guild.name})")
        
    channel_id = int("1172729342103654410")

    channel = client.get_channel(channel_id)
    if channel:
        tip_message = (
            "🚨 **TIP OF THE DAY** 🚨\n"
            f"**Match:** {match}\n"
            f"**Bet:** {bet}\n"
            f"**Quote:** {quote}\n"
            "**Betting Units:** TBD"
        )
        await channel.send(tip_message)
    else:
        print(f"Channel with ID {channel_id} not found.")

client.run(TOKEN)

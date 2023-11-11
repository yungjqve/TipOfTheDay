import os
import discord
import asyncio
from datetime import datetime, time, timedelta
from pytz import timezone
from dotenv import load_dotenv
import requests
from lxml import html

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

client = discord.Client(intents=intents)

last_tip_message = None  # Variable to store the last sent tip message

async def scrape_for_tips():
    url = 'https://wettbasis.com'
    response = requests.get(url)
    tree = html.fromstring(response.content)

    # Define your XPaths here
    xpath_match = '/html/body/div[1]/div[4]/div/div/main/article/div/div[1]/div[2]/div[3]/div[2]'
    xpath_bet = '/html/body/div[1]/div[4]/div/div/main/article/div/div[1]/div[2]/div[3]/div[3]'

    element_match = tree.xpath(xpath_match)
    element_bet = tree.xpath(xpath_bet)

    match = element_match[0].text_content().strip() if element_match else 'Element not found'
    bet = quote = 'Parent element not found'

    if element_bet:
        spans = element_bet[0].findall('.//span')
        bet = spans[0].text_content().strip() if len(spans) > 0 else 'First span not found'
        quote = spans[1].text_content().strip() if len(spans) > 1 else 'Second span not found'

    return match, bet, quote

async def send_daily_tip():
    global last_tip_message
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found.")
        return

    while not client.is_closed():
        now = datetime.now(timezone('Europe/Berlin'))
        target_time = datetime.combine(now.date(), time(0, 0))  # Set to 0:00
        if now.time() > target_time.time():
            target_time += timedelta(days=1)  # Move to the next day

        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        match, bet, quote = await scrape_for_tips()
        new_tip_message = (
            "🚨 **TIP OF THE DAY** 🚨\n"
            f"**Match:** {match}\n"
            f"**Bet:** {bet}\n"
            f"**Quote:** {quote}\n"
            "**Betting Units:** TBD"
        )

        # Check if the new tip message is similar to the last one
        if new_tip_message == last_tip_message:
            print("Similar tip detected, scheduling new scrape in 1 hour.")
            await asyncio.sleep(28800)  # Wait for 1 hour
            match, bet, quote = await scrape_for_tips()  # Rescrape for new tips
            new_tip_message = (
                "🚨 **TIP OF THE DAY** 🚨\n"
                f"**Match:** {match}\n"
                f"**Bet:** {bet}\n"
                f"**Quote:** {quote}\n"
                "**Betting Units:** TBD"
            )

        await channel.send(new_tip_message)
        last_tip_message = new_tip_message  # Update the last sent tip message

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds:
        print(f"Guild ID: {guild.id} (Name: {guild.name})")
    client.loop.create_task(send_daily_tip())

client.run(TOKEN)

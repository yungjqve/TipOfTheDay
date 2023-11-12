import discord
from tips_scraper import TipsScraper

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

async def send_tip(interaction: discord.Interaction):
    try:
        new_tip_message = await create_tip_message()

        await interaction.response.send_message(new_tip_message)
    except Exception as e:
        print(f"Error in send_tip command: {e}")

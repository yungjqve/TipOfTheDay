import discord
from tips_scraper import TipsScraper

scraper = TipsScraper()

async def create_tip_message():
    try:
        match, bet, quote, date, units, time, tournament = await scraper.scrape_for_tips()
        if "Element not found" in match:
            return "Today, there is no Tip Of The Day 😭"

        tip_message = (
            f"🚨 **TIP OF THE DAY {date}** 🚨\n"
            f"**Tournament: ** {tournament}\n"
            f"**Match:** {match}\n"
            f"**Time:** {time}\n"
            f"**Bet:** {bet}\n"
            f"**Quote:** {quote}\n"
            f"**Betting Units:** {units}"
        )
        return tip_message
    except Exception as e:
        print(f"Error in create_tip_message: {e}")
        return "An error occurred while creating the tip message."

async def send_tip(interaction: discord.Interaction):
    try:
        new_tip_message = await create_tip_message()
        await interaction.response.send_message(new_tip_message)
    except Exception as e:
        print(f"Error in send_tip command: {e}")
        await interaction.response.send_message("An error occurred while sending the tip.")


async def get_further_tips():
    try:
        await scraper.scrape_for_tips()  # This will set the url_for_further_tips
        return await scraper.get_further_tips()
    except Exception as e:
        print(f"Error in get_further_tips: {e}")
        return ["An error occurred while retrieving further tips."]
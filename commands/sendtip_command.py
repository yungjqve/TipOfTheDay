import discord
from discord.ui import Button, View
import logging
from utils.tips_scraper import TipsScraper

# Initialize logger
logging.basicConfig(level=logging.INFO)  # Or use logging.DEBUG for more verbose output
logger = logging.getLogger(__name__)

scraper = TipsScraper()

async def create_tip_message() -> str:
    try:
        async with TipsScraper() as scraper:
            date = await scraper.get_date()
            competition = await scraper.get_competition()
            match = await scraper.get_match()
            time = await scraper.get_time()
            bet = await scraper.get_bet()
            quote = await scraper.get_quote()
            units = await scraper.get_units()

        if "Element not found" in match:
            return "Today, there is no Tip Of The Day 😭"

        tip_message = (
            f"🚨 **TIP OF THE DAY {date}** 🚨\n"
            f"**Tournament: ** {competition}\n"
            f"**Match:** {match}\n"
            f"**Time:** {time}\n"
            f"**Bet:** {bet}\n"
            f"**Quote:** {quote}\n"
            f"**Betting Units:** {units}"
        )
        return tip_message
    except Exception as e:
        logger.error(f"Error in create_tip_message: {e}", exc_info=True)
        return "An error occurred while creating the tip message."

async def send_tip(interaction: discord.Interaction) -> None:
    try:
        new_tip_message = await create_tip_message()
        button = Button(label="View Further Tips", style=discord.ButtonStyle.primary, custom_id="view_further_tips")
        view = View()
        view.add_item(button)
        await interaction.response.send_message(new_tip_message, view=view)
    except Exception as e:
        logger.error(f"Error in send_tip command: {e}", exc_info=True)
        await interaction.response.send_message("An error occurred while sending the tip.")

async def get_further_tips() -> list:
    try:
        await scraper.scrape_for_tips()  # This will set the url_for_further_tips
        return await scraper.get_further_tips()
    except Exception as e:
        logger.error(f"Error in get_further_tips: {e}", exc_info=True)
        return ["An error occurred while retrieving further tips."]

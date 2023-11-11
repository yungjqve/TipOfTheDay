# Discord Betting Tips Bot

## Overview

This Discord bot automatically sends a daily betting tip to a specified Discord channel. It scrapes betting information from a website and formats it as a message in Discord.

## Features

- **Automated Daily Messages:** Sends a "Tip of the Day" message every day.
- **Web Scraping:** Extracts betting information from a website.
- **Customizable:** Easy to modify and extend.

## Installation

1. **Clone the Repository**

```bash
git clone https://github.com/yungjqve/TipOfTheDay
cd TipOfTheDay
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Setting Up the `.env`File**

- Create a file named **`.env`** in the root directory of the project.
- Add the following lines to the file:

```makefile
DISCORD_TOKEN='your_discord_token_here'
CHANNEL_ID=your_channel_id
```

4. **Running the Bot**

```bash
python bot.py
```

The bot will start and send the daily tip to the configured Discord channel.

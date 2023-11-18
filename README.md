# TipOfTheDay Discord Bot

## Introduction

TipOfTheDay is a Discord bot designed to provide daily betting tips to your Discord channel. It automatically scrapes and updates betting information from specified websites, offering users up-to-date betting insights directly within Discord.

## Features

- **Automated Daily Updates:** The bot scrapes selected betting websites daily to provide the latest tips.
- **Easy Integration:** Simple setup process for integrating the bot into any Discord channel.
- **Customizable Sources:** Option to specify or change the websites from which betting tips are sourced.

## Getting Started

1. **Clone the Repository**

```bash
git clone https://github.com/yungjqve/TipOfTheDay
cd TipOfTheDay
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Setting Up the `.env` File**

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

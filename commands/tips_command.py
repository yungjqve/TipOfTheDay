import os
import json
from lxml import html
from dotenv import load_dotenv
import pytz
from datetime import datetime
from discord import Embed
import aiohttp
import asyncio

league_ids_md = {
    'Premier League': 'premier-league-9',
    'Bundesliga': 'bundesliga-1',
    'Ligue 1': 'ligue-1-23',
    'Serie A': 'serie-a-13',
    'La Liga': 'laliga-10'
}

league_ids_tips = {
    'Premier League': '2021',
    'Bundesliga': '2002',
    'Ligue 1': '2015',
    'Serie A': '2019',
    'La Liga': '2014',
}

async def fetch(session, url):
    try:
        async with session.get(url, headers={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}) as response:
            if response.status == 403:
                print(f"Access denied when trying to access {url}")
                return None
            return await response.text()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def get_matchday(league_name):
    league_id = league_ids_md.get(league_name)
    url = f"https://onefootball.com/de/wettbewerb/{league_id}/spiele"

    async with aiohttp.ClientSession() as session:
        html_content = await fetch(session, url)
        if html_content:
            tree = html.fromstring(html_content)
            element = tree.xpath('/html/body/div[1]/main/div/div/div[6]/div/div/div[1]/div/div/h3')
            return element[0].text_content().strip().split('.')[0] if element else 'Element not found'
        else:
            return 'Failed to fetch data'

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'team_mappings.json')
with open(json_path, 'r', encoding='utf-8') as file:
    team_mappings = json.load(file)

async def get_all_links(league_name, matchday):
    load_dotenv()
    API = os.getenv('FOOTBALL_API')

    headers = {'X-Auth-Token': API}
    league_id = league_ids_tips.get(league_name)

    url = f'http://api.football-data.org/v4/competitions/{league_id}/matches?matchday={matchday}'

    async with aiohttp.ClientSession() as session:
        response = await session.get(url, headers=headers)
        data = await response.json()

        results = []
        match_info = []
        for match in data['matches']:
            home_team = team_mappings[league_name].get(match['homeTeam']['name'], match['homeTeam']['name'])
            away_team = team_mappings[league_name].get(match['awayTeam']['name'], match['awayTeam']['name'])
            matches = f"{home_team} - {away_team}"
            results.append(matches)

            utc_date = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
            utc_date = utc_date.replace(tzinfo=pytz.utc)  # Set timezone to UTC
            local_date = utc_date.astimezone(pytz.timezone('Europe/Berlin'))  # Adjust to local timezone if needed
            date_str = local_date.strftime('%d-%m-%Y')

            full_match_name = f"{match['homeTeam']['name']} vs {match['awayTeam']['name']}"

            # Construct the match URL with date
            match_url = f"https://www.wettbasis.com/sportwetten-tipps/{home_team}-vs-{away_team}-tipp-prognose-quoten-{date_str}"
            match_info.append((match_url, full_match_name))

        return match_info

def parse_element(tree, xpath):
    element = tree.xpath(xpath)
    return element[0].text_content().strip() if element else 'Element not found'

async def get_tips(session, url):
    try:
        async with session.get(url, headers={'User-Agent': 'Your User Agent'}) as response:
            if response.status == 200:
                content = await response.text()
                tree = html.fromstring(content)

                tips_and_risks = []
                for i in range(1, 4):  # Assuming there are 3 tips and risks
                    tip_xpath = f'/html/body/div[1]/div[4]/div/div/main/article/div[2]/div[2]/table/tbody/tr[{i}]/td[1]'
                    risk_xpath = f'/html/body/div[1]/div[4]/div/div/main/article/div[2]/div[2]/table/tbody/tr[{i}]/td[4]'

                    tip = parse_element(tree, tip_xpath)
                    risk = parse_element(tree, risk_xpath)

                    tips_and_risks.append((tip, risk))

                return tips_and_risks
            else:
                return []
    except Exception as e:
        print(f"An error occurred while fetching tips: {e}")
        return []

async def get_all_tips_for_league(league_name, matchday):
    match_info = await get_all_links(league_name, matchday)
    all_tips = {}

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url, match_name in match_info:
            task = asyncio.ensure_future(get_tips(session, url))
            tasks.append(task)

        tips_responses = await asyncio.gather(*tasks)

        for (url, match_name), tips in zip(match_info, tips_responses):
            if tips:
                all_tips[match_name] = tips

    return all_tips

async def create_tips_embed(league_name):
    # Await the result of get_matchday if it's an asynchronous function
    matchday = await get_matchday(league_name)
    all_tips = await get_all_tips_for_league(league_name, int(matchday))

    # Check if there are any tips
    if not all_tips:
        # Handle the case where there are no tips
        all_tips = await get_all_tips_for_league(league_name, int(matchday) - 1)

    # Now it's safe to access the first match's tips
    first_match_tips = next(iter(all_tips.values()))
    if first_match_tips and first_match_tips[0][0] == 'Element not found':
        # If no tips found for the current matchday, get tips for the previous matchday
        all_tips = await get_all_tips_for_league(league_name, int(matchday) - 1)
        matchday = str(int(matchday) - 1)  # Update matchday for the embed title

    embed = Embed(title=f"{league_name} - Matchday {matchday} Tips", color=0x1a75ff)

    for match_name, tips in all_tips.items():
        tips_str = "\n".join([f"Tip: {tip}, Risk: {risk}" for tip, risk in tips])
        embed.add_field(name=match_name, value=tips_str, inline=False)

    return embed
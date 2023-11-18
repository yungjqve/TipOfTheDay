import requests
import os
from dotenv import load_dotenv
from discord import Embed

league_ids = {
    'Premier League': '2021',
    'Bundesliga': '2002',
    'Ligue 1': '2015',
    'Serie A': '2019',
    'La Liga': '2014'
}

def get_match_results(league_name, matchday):
    load_dotenv()
    API = os.getenv('FOOTBALL_API')

    headers = {'X-Auth-Token': API}
    league_id = league_ids.get(league_name)

    url = f'http://api.football-data.org/v4/competitions/{league_id}/matches?matchday={matchday}'
    response = requests.get(url, headers=headers)
    data = response.json()

    results = []
    for match in data['matches']:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        score = match['score']['fullTime']

        match_result = f"{home_team} vs {away_team} - Score: {score['home']}:{score['away']}"
        results.append(match_result)
    
    return results

def create_results_embed(league, matchday):
    try:
        # Check for valid matchday range
        if matchday < 1 or matchday > 38:
            return "Please enter a valid matchday (usually between 1 and 38)."

        results = get_match_results(league, matchday)
        if not results:
            return "No matches found for this matchday in the selected league."

        # Check for future matchdays
        if any('None:None' in result for result in results):
            return "This matchday hasn't been played yet."

        embed = Embed(title=f"Football Results for Matchday {matchday} in {league}",
                      description="Here are the match results:",
                      color=0x1a5e9a)

        for result in results:
            match_info, score = result.split(' - Score: ')
            embed.add_field(name=match_info, value=f"Score: {score}", inline=False)

        return embed

    except Exception as e:
        print(f"Error in create_results_embed: {e}")
        return "Failed to retrieve results."
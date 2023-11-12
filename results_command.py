import requests
import os
from dotenv import load_dotenv

league_ids = {
    'Premier League': '2021',
    'Bundesliga': '2002',
    'Ligue 1': '2015',
    'Serie A': '2019',
    'Eredivisie': '2003',
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
import aiohttp
from lxml import html
import logging
from bs4 import BeautifulSoup

class TipsScraper:
    def __init__(self):
        self.base_url = 'https://wettbasis.com'
        logging.basicConfig(level=logging.INFO)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def fetch_page(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logging.error(f"Error fetching page: HTTP Status {response.status}")
                    return None
        except Exception as e:
            logging.error(f"Error in fetch_page: {e}")
            raise

    async def get_date(self):
        html_content = await self.fetch_page(self.base_url)
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.select_one('.wettbasis-tipps-betslip__row span:nth-of-type(2)').text

    async def get_competition(self):
        html_content = await self.fetch_page(self.base_url)
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.select_one('.wettbasis-tipps-betslip__event .fw-400 span').text
    
    async def get_match(self):
        html_content = await self.fetch_page(self.base_url)
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.select_one('.wettbasis-tipps-betslip__event .wettbasis-tipps-betslip__row:nth-of-type(2) span').text

    async def get_time(self):
        html_content = await self.fetch_page(self.base_url)
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.select_one('.wettbasis-tipps-betslip__event .fw-400 span:nth-of-type(2)').text

    async def get_bet(self):
        html_content = await self.fetch_page(self.base_url)
        soup = BeautifulSoup(html_content, 'html.parser')
        bet_part1 = soup.select_one('.wettbasis-tipps-betslip__event .uppercased').contents[0].strip()
        bet_part2 = soup.select_one('.wettbasis-tipps-betslip__event .uppercased span').text.strip()
        return f"{bet_part1} {bet_part2}"

    async def get_quote(self):
        html_content = await self.fetch_page(self.base_url)
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.select_one('.wettbasis-tipps-betslip__event .wettbasis-tipps-betslip__row:last-child span:nth-of-type(2)').text
    
    async def get_units(self):
        url = await self.generate_url(await self.get_match(), await self.get_date())
        html_content = await self.fetch_page(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        all_details_data = soup.find_all('span', class_='details-data')
        stake_span = all_details_data[2]
        stake_text = stake_span.get_text(strip=True)
        return stake_text.split()[-1]

    async def generate_url(self, match, date):
        formatted_match = match.lower().replace(' - ', '-vs-').replace(' ', '-')
        formatted_date = date.replace('.', '-')
        url_match =  f"https://www.wettbasis.com/sportwetten-tipps/{formatted_match}-tipp-prognose-quoten-{formatted_date}"
        
        return url_match
    
    async def get_further_tips(self):   
        try:
            url = await self.generate_url(await self.get_match(), await self.get_date())
            html_content = await self.fetch_page(url)
            tree = html.fromstring(html_content)

            tips_and_risks = []
            for i in range(1, 4):  # Assuming there are 3 tips and risks
                tip_xpath = f'/html/body/div[1]/div[4]/div/div/main/article/div[2]/div[2]/table/tbody/tr[{i}]/td[1]'
                risk_xpath = f'/html/body/div[1]/div[4]/div/div/main/article/div[2]/div[2]/table/tbody/tr[{i}]/td[4]'

                tip = self.parse_element(tree, tip_xpath)
                risk = self.parse_element(tree, risk_xpath)

                tips_and_risks.extend([tip, risk])

            return tips_and_risks
        except Exception as e:
            logging.error(f"Error in get_further_tips: {e}")
            return ['Error occurred']
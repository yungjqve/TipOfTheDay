import requests
from lxml import html

class TipsScraper:
    def __init__(self):
        self.base_url = 'https://wettbasis.com'

    async def scrape_for_tips(self):
        response = await self.fetch_page(self.base_url)
        tree = html.fromstring(response.content)

        match = self.parse_element(tree, '/html/body/div[1]/div[4]/div/div/main/article/div/div[1]/div[2]/div[3]/div[2]')
        date = self.parse_date(tree)
        bet, quote = self.parse_bet(tree)

        url_match = await self.generate_url(match, date)
        units = await self.scrape_units(url_match)

        return match, bet, quote, date, units

    async def fetch_page(self, url):
        response = requests.get(url)
        return response

    def parse_element(self, tree, xpath):
        element = tree.xpath(xpath)
        return element[0].text_content().strip() if element else 'Element not found'

    def parse_date(self, tree):
        element_date = tree.xpath('/html/body/div[1]/div[4]/div/div/main/article/div/div[1]/div[2]/div[1]/div[3]')
        if element_date:
            date_spans = element_date[0].findall('.//span')
            return date_spans[1].text_content().strip().replace('\n', ' ')
        return 'Date not found'

    def parse_bet(self, tree):
        element_bet = tree.xpath('/html/body/div[1]/div[4]/div/div/main/article/div/div[1]/div[2]/div[3]/div[3]')
        if element_bet:
            spans = element_bet[0].findall('.//span')
            if len(spans) > 2:
            # Concatenate all but the last span for 'bet', removing new lines
                bet = ' '.join(span.text_content().strip().replace('\n', ' ') for span in spans[:-2])
                quote = spans[-1].text_content().strip().replace('\n', ' ')  # Use the last span for 'quote'
                return bet, quote
            elif len(spans) == 2:
                bet = spans[0].text_content().strip().replace('\n', ' ')
                quote = spans[1].text_content().strip().replace('\n', ' ')
                return bet, quote

        return 'Bet not found', 'Quote not found'

    async def scrape_units(self, url_match):
        response = await self.fetch_page(url_match)
        tree = html.fromstring(response.content)
        xpath_units = '/html/body/div[1]/div[3]/div[2]/div/div[5]/span[2]'
    
        try:
            element_units = tree.xpath(xpath_units)
            if not element_units:
                return 'Units element not found'

            units_text = element_units[0].text_content().strip()
            cleaned_units = units_text.strip("[]").replace("'", "")
            units = ''.join(cleaned_units.split(',')).strip()
            return units

        except Exception as e:
            return f'Error occurred: {str(e)}'

    async def generate_url(self, match, date):
        formatted_match = match.lower().replace(' - ', '-vs-').replace(' ', '-')
        formatted_date = date.replace('.', '-')
        url_match =  f"https://www.wettbasis.com/sportwetten-tipps/{formatted_match}-tipp-prognose-quoten-{formatted_date}"
        return url_match
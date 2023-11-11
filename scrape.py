import requests
from lxml import html

url = 'https://wettbasis.com'

response = requests.get(url)
tree = html.fromstring(response.content)
xpath_match = '/html/body/div[1]/div[4]/div/div/main/article/div/div[1]/div[2]/div[3]/div[2]'
xpath_bet = '/html/body/div[1]/div[4]/div/div/main/article/div/div[1]/div[2]/div[3]/div[3]'

element_match = tree.xpath(xpath_match)
element_bet = tree.xpath(xpath_bet)

match = element_match[0].text_content().strip() if element_match else 'Element not found'

if element_bet:
    # Extract the first and second span elements
    spans = element_bet[0].findall('.//span')
    bet = spans[0].text_content().strip() if len(spans) > 0 else 'First span not found'
    quote = spans[1].text_content().strip() if len(spans) > 1 else 'Second span not found'
else:
    bet = quote = 'Parent element not found'


import logging

from bs4 import BeautifulSoup
from scraper import Scraper

log = logging.getLogger(__name__)


class Aldi:
    def __init__(self):
        self.name = "Aldi"
        self.logo = "Test"
        self.base_url = f"https://groceries.aldi.co.uk/en-GB/"

    def filter_categories(self, html):
        soup = BeautifulSoup(html, "html.parser")
        supermarket_categories = []

        for litag in soup.find_all('li', {'class': 'submenu'}):
            category = {}
            for category_name in litag.find('a', {'class': 'dropdown-item'}):
                if 'SHOP ALL' in category_name:
                    category['name'] = category_name[9:].lower()
            for category_part_url in litag.find_all('a', href=True):
                if 'shopall' in category_part_url.get('href'):
                    category['part_url'] = category_part_url.get('href')
            supermarket_categories.append(category)

        supermarket_categories = [d for d in supermarket_categories if d]
        return supermarket_categories


aldi = Aldi()
scraper = Scraper(aldi, database=None)

html = scraper.get_html(aldi.base_url)
a = aldi.filter_categories(html)
print(a)

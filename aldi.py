import logging

from bs4 import BeautifulSoup
from supermarkets import Supermarkets
from scraper import Scraper

log = logging.getLogger(__name__)


class Aldi(Supermarkets):
    def __init__(self):
        super().__init__()
        self.name = "Aldi"
        self.logo = "https://cdn.aldi-digital.co.uk/32FDVWu4Lhbxgj9Z3v03ji0pGJIp?&w=70&h=84"
        self.base_url = "https://groceries.aldi.co.uk"

    def build_url(self, url, page):
        return url + f"&page={page}"


    def filter_categories(self, html):
        soup = BeautifulSoup(html, "html.parser")
        supermarket_categories = []

        for litag in soup.find_all('li', {'class': 'submenu'}):
            category = {}
            for category_name in litag.find('a', {'class': 'dropdown-item'}):
                if 'SHOP ALL' in category_name:
                    category_name = category_name[9:].lower()
                    category['name'] = category_name.strip()

            for category_part_url in litag.find_all('a', href=True):
                if 'shopall' in category_part_url.get('href'):
                    hyperlink_string = category_part_url.get('href')
                    length = hyperlink_string.find("?")
                    category['part_url'] = hyperlink_string[:length + 1]

            supermarket_categories.append(category)

        supermarket_categories = [d for d in supermarket_categories if d]
        return supermarket_categories

    def filter_products(self, html):
        soup = BeautifulSoup(html, "html.parser")
        supermarket_category_products = []

        for divtag in soup.find_all('div', {'class': 'col-6'}):
            product = {}
            for product_name in divtag.find():
                pass

    def return_product_name(self, html):
        soup = BeautifulSoup(html, "html.parser")
        product_names = []

        for divtag in soup.find_all('div', {'class': 'image-tile'}):
            for product_name in divtag.find('a', {'class': 'p text-default-font'}):
                print(product_name)

    def return_stock_images(self, html):
        soup = BeautifulSoup(html, "html.parser")
        stock_images = []
        try:
            for litag in soup.find_all('div', {'class': 'image-tile'}):
                for stock_image in litag.find_all('img'):
                    stock_images.append(stock_image.get('src'))
        except TypeError as e:
            log.error(f"Filter type exception: {e}")
        except Exception as e:
            log.error(f"Filter exception: {e}")
        return stock_images

        #return product_names

# aldi = Aldi()
# scraper = Scraper(aldi, database=None)

# html = scraper.get_html(aldi.base_url)
# a = aldi.filter_categories(html)
# print(a)
# y = aldi.get_id()
# print(y)
# categories = aldi.get_categories()
# for category in categories:
#   category_name = category[2]
#  category_information = aldi.get_category_information(category_name)
# print(category_information)
# print(category_information[1])
# print(type(category_information[1]))
# break


# print(type(x))
# z = aldi.get_category_information('specially selected')
# print(z)
# print(type(x))

aldi = Aldi()
url = "https://groceries.aldi.co.uk/en-GB/bakery?"
scraper = Scraper(aldi, database=None)
html = scraper.get_html(url)
x = aldi.return_stock_images(html)
print(x)
#print(product_names)
import logging
import unicodedata
import re

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

        supermarket_categories = [dictionary for dictionary in supermarket_categories if dictionary]
        return supermarket_categories

    def filter_products(self, html):
        soup = BeautifulSoup(html, "html.parser")
        supermarket_category_products = []

        for divtag in soup.find_all('div', {'class': 'product-tile'}):
            product = {}
            for product_name in divtag.find('a', {'class': 'p text-default-font'}):
                product['name'] = product_name
            for product_price in divtag.find('span', {'class': 'h4'}):
                product['price'] = self.format_product_price(product_price.string)
            for product_part_url in divtag.find('div', 'image-tile'):
                try:
                    product_part_url = product_part_url.get('href')
                    if product_part_url is not None:
                        product['part_url'] = product_part_url
                except AttributeError:
                    pass
            for product_image in divtag.find('figure'):
                product['image'] = product_image.get('src')
            supermarket_category_products.append(product)

        return self.format_supermarket_category_products(supermarket_category_products)

    def filter_product_details(self, html):
        soup = BeautifulSoup(html, "html.parser")
        product_details = {}
        allergy_list = []

        for table_row in soup.find('tbody'):
            if "Ingredients" in table_row.get_text():
                ingredients_text = table_row.get_text().replace("Ingredients", "").strip()
                ingredients_text = unicodedata.normalize("NFKC", ingredients_text)
                for allergen in self.get_allergens():
                    if ingredients_text.lower().find(allergen) >= 0:
                        allergy_list.append(allergen)

            if "Allergy advice" in table_row.get_text():
                allergy_text = table_row.get_text().replace("Allergy advice", "").strip()
                for allergen in self.get_allergens():
                    if allergy_text.lower().find(allergen) >= 0:
                        allergy_list.append(allergen)
                product_details['allergens'] = allergy_list

            if "Nutrition information" in table_row.get_text():
                nutrition_text = table_row.get_text().replace("Nutrition information", "").strip()
                matches = re.findall(self.get_nutrition_pattern(), nutrition_text)
                energy_kj, energy_kcal, fat, sat_fat, carb, sugars, fibre, protein, salt = matches[0]
                product_details['energy_kj'] = float(energy_kj.replace("kJ", ""))
                product_details['energy_kcal'] = float(energy_kcal.replace("kcal", ""))
                product_details['fat'] = float(fat)
                product_details['of_which_saturates'] = float(sat_fat)
                product_details['carbohydrates'] = float(carb)
                product_details['of_which_sugars'] = float(sugars)
                product_details['fibre'] = float(fibre)
                product_details['protein'] = float(protein)
                product_details['salt'] = float(salt)

        return product_details

    def format_product_image_src(self, src):
        char_to_replace = "\\"
        return src.replace(char_to_replace, "/")

    def format_product_price(self, price_string):
        char_to_remove = "£"
        price_string = price_string.replace(char_to_remove, "")
        return float(price_string)

    def format_supermarket_category_products(self, product_list):
        for product in product_list:
            product.update({'image': self.format_product_image_src(product['image'])})
        return product_list

#aldi = Aldi()
#url = "https://groceries.aldi.co.uk/en-GB/p-village-bakery-toastie-thick-sliced-white-bread-800g/4088600253305"
#scraper = Scraper(aldi, database=None)
#html = scraper.get_html(url)
#x = aldi.filter_product_details(html)
#print(x)

import logging
import re

import unicodedata
from bs4 import BeautifulSoup
from scraper import Scraper
from supermarkets import Supermarkets

log = logging.getLogger(__name__)


class Morrisons(Supermarkets):
    def __init__(self):
        super().__init__()
        self.name = Morrisons
        self.logo = "https://groceries.morrisons.com/static/morrisonslogo-fe24a.svg"
        self.base_url = "https://groceries.morrisons.com"
        log.info(f"{self.name} loaded")

    def filter_categories(self, html):
        if html is not None:
            soup = BeautifulSoup(html, "html.parser")
            supermarket_categories = []

            try:
                for litag in soup.find_all('li', {'class': 'level-item has-children'}):
                    category = {}
                    for category_name in litag.find('a'):
                        category['name'] = category_name

                    for category_part_url in litag.find_all('a', href=True):
                        hyperlink_string = category_part_url.get('href')
                        length = hyperlink_string.find("?")
                        category['part_url'] = hyperlink_string[:length]

                    supermarket_categories.append(category)
                supermarket_categories = [dictionary for dictionary in supermarket_categories if dictionary]
                return supermarket_categories

            except Exception as e:
                log.error(f"Error filtering categories for {self.name}: {e}")
                return []
        else:
            log.error(f"Page was not found: category html for {self.name} was not parsed correctly")
            return []

    def filter_products(self, html):
        if html is not None:
            try:
                soup = BeautifulSoup(html, "html.parser")
                supermarket_category_products = []

                for divtag in soup.find_all('div', {'class': 'fop-contentWrapper'}):
                    product = {}

                    # Extract product name
                    product_name_tag = divtag.find('h4', {'class': 'fop-title'}).find('span')
                    if product_name_tag:
                        product['name'] = product_name_tag.get_text(strip=True)

                    # Extract product price
                    product_price_tag = divtag.find('span', {'class': 'fop-price'})
                    if product_price_tag:
                        product_price_text = product_price_tag.string
                        if "p" in product_price_text:
                            product_price_text = "0." + product_price_text
                            product['price'] = self.format_product_price_pence(product_price_text)
                        else:
                            product['price'] = self.format_product_price_pound(product_price_text)

                    # Extract product part URL
                    product_part_url_tag = divtag.find('a', href=True)
                    if product_part_url_tag:
                        product_part_url = product_part_url_tag.get('href')
                        product['part_url'] = product_part_url

                    # Extract product image URl
                    product_image_tag = divtag.find('img', {'class': 'fop-img'})
                    if product_image_tag:
                        product['image'] = "https://groceries.morrisons.com" + product_image_tag.get('src')

                    supermarket_category_products.append(product)

                return self.format_supermarket_category_products(supermarket_category_products)
            except Exception as e:
                log.error(f"Error filtering products for {self.name}: {e}")
                return []
        else:
            log.error(f"Page was not found: product html for {self.name} was not passed correctly")
            return []

    def filter_product_details(self, html):
        soup = BeautifulSoup(html, "html.parser")
        product_details = {}
        allergy_list = []

        # Extract product allergens
        for divtag in soup.find_all('div', {'class': 'bop-info__content'}):
            allergens_text = divtag.get_text(strip=True)
            allergens_text = unicodedata.normalize("NFKC", allergens_text)
            for allergen in self.allergens:
                if allergens_text.lower().find(allergen) >= 0:
                    allergy_list.append(allergen)

            product_details['allergens'] = list(set(allergy_list))

        # Extract product nutritional information
        for table_row in soup.find('tbody'):
            nutrition_text = table_row.get_text(strip=True)
            print(nutrition_text)
            values = self.format_nutritional_information(nutrition_text)
            # Use find_next()
            try:
                energy_kj, energy_kcal, fat, sat_fat, carb, sugars, fibre, protein, salt = values
                product_details['energy_kj'] = float(energy_kj.replace("kj", ""))
                product_details['energy_kcal'] = float(energy_kcal.replace("kcal", ""))
                product_details['fat'] = float(fat)
                product_details['of_which_saturates'] = float(sat_fat)
                product_details['carbohydrates'] = float(carb)
                product_details['of_which_sugars'] = float(sugars)
                product_details['fibre'] = float(fibre)
                product_details['protein'] = float(protein)
                product_details['salt'] = float(salt)
            except ValueError as e:
                log.error(f"Error processing nutritional values: {e}")
                product_details['energy_kj'] = 0.0
                product_details['energy_kcal'] = 0.0
                product_details['fat'] = 0.0
                product_details['of_which_saturates'] = 0.0
                product_details['carbohydrates'] = 0.0
                product_details['of_which_sugars'] = 0.0
                product_details['fibre'] = 0.0
                product_details['protein'] = 0.0
                product_details['salt'] = 0.0

        return product_details if product_details else None

    def format_nutritional_information(self, nutrition_text):
        formatted_values = []
        matches = re.findall(self.nutrition_pattern, nutrition_text)

        if matches:
            if len(matches) == 2 or len(matches) == 9:
                nutritional_labels = ["energy_kj", "energy_kcal", "fat", "fat_sat", "carb", "sugars", "fibre",
                                      "protein",
                                      "salt"]
                default_value = 0
                for label in nutritional_labels:
                    try:
                        value = matches[nutritional_labels.index(label)][1]
                        if value == '':
                            log.warning(f"Value for {nutritional_labels.index(label)} was not found")
                            raise ValueError
                        else:
                            formatted_values.append(value)
                    except ValueError:
                        log.info(f"Setting default value for {label}")
                        formatted_values.append(str(default_value))
            else:
                log.warning(f"Nutritional information was not in valid format")
                formatted_values = ['0', '0', '0', '0', '0', '0', '0', '0', '0']
        else:
            log.warning(f"Match was not found")
            formatted_values = ['0', '0', '0', '0', '0', '0', '0', '0', '0']

        return formatted_values

    def get_nutrition_pattern(self):
        return (r"([(]?[kK][jJ][)]?|[(]?kcal[)]?|Fat|of which Saturates|Carbohydrate|of which "
                r"Sugars|Fibre|Protein|Salt)([\s]?[<]?\d\d\d|[\s]?[<]?\d+[.]?\d+)")


"""
# Testing filter_categories
scraper = Scraper(supermarkets=None, database=None)
morrisons = Morrisons()
url = "https://groceries.morrisons.com/browse"
html = scraper.get_html(url)
x = morrisons.filter_categories(html)
print(x)
"""

"""
# Testing filter_products
scraper = Scraper(supermarkets=None, database=None)
morrisons = Morrisons()
url = "https://groceries.morrisons.com/browse/bakery-cakes-102210"
html = scraper.get_html(url)
x = morrisons.filter_products(html)
print(x)
"""

#"""
# Testing filter_product_details
scraper = Scraper(supermarkets=None, database=None)
morrisons = Morrisons()
url = "https://groceries.morrisons.com/products/mcvitie-s-digestives-chocolate-slices-368057011"
html = scraper.get_html(url)
x = morrisons.filter_product_details(html)
print(x)
#"""

"""
# Testing nutrition pattern regex
nutritional_info = "Typical ValuesPer 100gPer Slice (25.9g) Energy (kJ)2066535 (kcal)494128 Fat25.1g6.5g of which Saturates12.4g3.2g Carbohydrate61.2g15.9g of which Sugars36.3g9.4g Fibre2.1g0.6g Protein4.6g1.2g Salt0.80g0.21g Typical number of slices per pack: 5"
pattern = (r"([(]?[kK][jJ][)]?|[(]?kcal[)]?|Fat|of which Saturates|Carbohydrate|of which "
           r"Sugars|Fibre|Protein|Salt)([\s]?[<]?\d\d\d|[\s]?[<]?\d+[.]?\d+)")
#matches = re.findall(pattern, nutritional_info)
#print(matches)
#for match in matches:
#    print(match[1])
"""

"""
# Testing format_nutritional_information
nutritional_info = "Typical ValuesPer 100gPer Slice (25.9g) Energy (kJ)2066535 (kcal)494128 Fat25.1g6.5g of which Saturates12.4g3.2g Carbohydrate61.2g15.9g of which Sugars36.3g9.4g Fibre2.1g0.6g Protein4.6g1.2g Salt0.80g0.21g Typical number of slices per pack: 5"
pattern = (r"([(]?[kK][jJ][)]?|[(]?kcal[)]?|Fat|of which Saturates|Carbohydrate|of which "
           r"Sugars|Fibre|Protein|Salt)([\s]?[<]?\d\d\d|[\s]?[<]?\d+[.]?\d+)")
formatted_values = []
matches = re.findall(pattern, nutritional_info)

if matches:
    if len(matches) == 2 or len(matches) == 9:
        nutritional_labels = ["energy_kj", "energy_kcal", "fat", "fat_sat", "carb", "sugars", "fibre",
                              "protein",
                              "salt"]
        default_value = 0
        for label in nutritional_labels:
            try:
                value = matches[nutritional_labels.index(label)][1]
                if value == '':
                    log.warning(f"Value for {nutritional_labels.index(label)} was not found")
                    raise ValueError
                else:
                    formatted_values.append(value)
            except ValueError:
                log.info(f"Setting default value for {label}")
                formatted_values.append(str(default_value))
    else:
        log.warning(f"Nutritional information was not in valid format")
        formatted_values = ['0', '0', '0', '0', '0', '0', '0', '0', '0']
else:
    log.warning(f"Match was not found")
    formatted_values = ['0', '0', '0', '0', '0', '0', '0', '0', '0']

print(formatted_values)
"""

"""
# Testing format_nutritional_information
morrisons = Morrisons()
nutritional_info = "Typical ValuesPer 100gPer Slice (25.9g) Energy (kJ)2066535 (kcal)494128 Fat25.1g6.5g of which Saturates12.4g3.2g Carbohydrate61.2g15.9g of which Sugars36.3g9.4g Fibre2.1g0.6g Protein4.6g1.2g Salt0.80g0.21g Typical number of slices per pack: 5"
formatted_details = morrisons.format_nutritional_information(nutritional_info)
print(formatted_details)
"""

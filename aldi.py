import logging
import unicodedata
import re

from scraper import Scraper
from bs4 import BeautifulSoup
from supermarkets import Supermarkets

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
        if html is not None:
            soup = BeautifulSoup(html, "html.parser")
            supermarket_categories = []

            try:
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
            except Exception as e:
                log.error(f"Error filtering {self.name} categories: {e}")
                return []
        else:
            log.error(f"Page was not found: category html for {self.name} was not passed correctly")
            return []

    def filter_products(self, html):
        if html is not None:
            soup = BeautifulSoup(html, "html.parser")
            supermarket_category_products = []
            try:
                for divtag in soup.find_all('div', {'class': 'product-tile'}):
                    product = {}
                    for product_name in divtag.find('a', {'class': 'p text-default-font'}):
                        product['name'] = product_name
                    for product_price in divtag.find('span', {'class': 'h4'}):
                        product['price'] = self.format_product_price_pound(product_price.string)
                    for product_part_url in divtag.find('div', 'image-tile'):
                        try:
                            product_part_url = product_part_url.get('href')
                            if product_part_url is not None:
                                product['part_url'] = product_part_url
                        except AttributeError as e:
                            log.warning(f"Error filtering part_url for {product['name']}: {e}")
                            continue
                    for product_image in divtag.find('figure'):
                        product['image'] = product_image.get('src')
                    supermarket_category_products.append(product)

                return self.format_supermarket_category_products(supermarket_category_products)
            except Exception as e:
                log.error(f"Error filtering products for {self.name}: {e}")
                return []
        else:
            log.error(f"Page was not found: product html for {self.name} was not passed correctly")
            return []

    def filter_product_details(self, html):
        if html is not None:
            soup = BeautifulSoup(html, "html.parser")
            allergy_list = []

            try:
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
                        allergy_list = list(set(allergy_list))

                    if "Nutrition information" in table_row.get_text():
                        nutrition_text = table_row.get_text().replace("Nutrition information", "").strip()
                        values = self.format_nutritional_information(nutrition_text)
                        product_details = self.assign_product_values(values, allergy_list)
                        if product_details is None:
                            product_details = self.assign_default_values(allergy_list)

                        return product_details if product_details else None

            except Exception as e:
                log.error(f"Error filtering product details for {self.name}: {e}")
                return None
        else:
            log.error(f"Page was not found: product information html for {self.name }was not passed correctly")
            return None

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
                    if label == "energy_kj" or label == "energy_kcal":
                        try:
                            value = matches[nutritional_labels.index(label)][2].lower()
                            if value == '':
                                log.warning(
                                    f"Value for {nutritional_labels[nutritional_labels.index(label) + 1]} may be "
                                    f"incorrect")
                                raise ValueError
                            else:
                                formatted_value = str(value).replace("<", "").strip()
                                formatted_value = str(formatted_value).replace(".", "").strip()
                                formatted_values.append(formatted_value)
                        except ValueError:
                            log.error(f"Value not found for {label}, setting default value.")
                            formatted_values.append(str(default_value))
                    else:
                        try:
                            value = matches[nutritional_labels.index(label)][1]
                            formatted_value = str(value).replace("<", "").strip()
                            formatted_values.append(formatted_value)
                        except IndexError:
                            log.error(f"Value not found for {label}, setting default value.")
                            formatted_values.append(str(default_value))
            else:
                log.warning("Nutritional information was not in valid format")
                formatted_values = ['0', '0', '0', '0', '0', '0', '0', '0', '0']
        else:
            log.warning("Match was not found")
            formatted_values = ['0', '0', '0', '0', '0', '0', '0', '0', '0']

        return formatted_values

    def assign_product_values(self, nutritional_values, allergens):
        product_details = {}

        try:
            energy_kj, energy_kcal, fat, sat_fat, carb, sugars, fibre, protein, salt = nutritional_values
            product_details['energy_kj'] = float(energy_kj.replace("kj", ""))
            product_details['energy_kcal'] = float(energy_kcal.replace("kcal", ""))
            product_details['fat'] = float(fat)
            product_details['of_which_saturates'] = float(sat_fat)
            product_details['carbohydrates'] = float(carb)
            product_details['of_which_sugars'] = float(sugars)
            product_details['fibre'] = float(fibre)
            product_details['protein'] = float(protein)
            product_details['salt'] = float(salt)
            product_details['allergens'] = list(allergens)

            return product_details

        except ValueError as e:
            log.error(f"Error processing nutritional values: {e}")
            return None

        except Exception as ex:
            log.error(f"An error occurred while trying to process product details for a {self.name} product: {ex}")
            return None

    def get_nutrition_pattern(self):
        return (r"(Fat|of which saturates|Carbohydrate|of which sugars|Fibre|Protein|Salt)(\s+[<]?\d+[.]?\d+|\s+\d+)|("
                r"\d+[.]?[kK][jJ]|\d+[.]?kcal)")


scraper = Scraper(supermarkets=None, database=None)
url = "https://groceries.aldi.co.uk/en-GB/p-village-bakery-toastie-thick-sliced-white-bread-800g/4088600253305"
html = scraper.get_html(url)
aldi = Aldi()
x = aldi.filter_product_details(html)
print(x)

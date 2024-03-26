import logging
import unicodedata

from bs4 import BeautifulSoup

from supermarkets import Supermarkets

log = logging.getLogger(__name__)


class Morrisons(Supermarkets):
    def __init__(self):
        super().__init__()
        self.name = "Morrisons"
        self.logo = "https://groceries.morrisons.com/static/morrisonslogo-fe24a.svg"
        self.base_url = "https://groceries.morrisons.com/browse"
        log.info(f"{self.name} loaded")

    def build_url(self, url, page):
        return False

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
                        category['part_url'] = hyperlink_string[:length].replace("/browse", "")

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
            soup = BeautifulSoup(html, "html.parser")
            supermarket_category_products = []
            try:
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
                        product['part_url'] = product_part_url.replace("/browse", "")

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
        if html is not None:
            soup = BeautifulSoup(html, "html.parser")
            allergy_list = []
            try:
                # Extract product allergens
                for divtag in soup.find_all('div', {'class': 'bop-info__content'}):
                    allergens_text = divtag.get_text(strip=True)
                    allergens_text = unicodedata.normalize("NFKC", allergens_text)
                    for allergen in self.allergens:
                        if allergens_text.lower().find(allergen) >= 0:
                            allergy_list.append(allergen)

                    allergy_list = list(set(allergy_list))

                # Extract product nutritional information
                nutrients_table = soup.find('tbody')
                values = self.format_nutritional_information(nutrients_table)
                product_details = self.assign_product_values(values, allergy_list)
                if product_details is None:
                    product_details = self.assign_default_values(allergy_list)
                return product_details if product_details else None

            except Exception as e:
                log.error(f"Error filtering product details for {self.name}: {e}")
                return None
        else:
            log.error(f"Page was not found: product information html for {self.name} was not passed correctly")
            return None

    def format_nutritional_information(self, nutrition_text):
        nutritional_information = []
        try:
            for row in nutrition_text.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 2:
                    nutrient = cols[0].get_text(strip=True)
                    value_per_100g = cols[1].get_text(strip=True)
                    nutritional_information.append((nutrient, value_per_100g))
            nutritional_information.pop(-1)
            return [value.replace("g", "") for _, value in nutritional_information]
        except Exception as e:
            log.error(f"Error trying to format nutritional information for {self.name}: {e}")
            return []

    def get_nutrition_pattern(self):
        return (r"([(]?[kK][jJ][)]?|[(]?kcal[)]?|Fat|of which Saturates|Carbohydrate|of which "
                r"Sugars|Fibre|Protein|Salt)([\s]?[<]?\d\d\d|[\s]?[<]?\d+[.]?\d+)")

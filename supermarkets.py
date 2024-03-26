import logging
import re

from database import Database

db = Database()
log = logging.getLogger(__name__)


class Supermarkets:
    def __init__(self):
        self.name = ""
        self.logo = ""
        self.base_url = ""
        self.id = None
        self.categories = self.get_categories()
        self.allergens = self.get_allergens()
        self.nutrition_pattern = self.get_nutrition_pattern()

    def build_url(self, url, page):
        return ""

    def filter_categories(self, html):
        return []

    def filter_products(self, html):
        return []

    def filter_product_details(self, html):
        return {}

    def assign_product_values(self, nutritional_values, allergens):
        product_details = {}

        try:
            energy_kj, energy_kcal, fat, sat_fat, carb, sugars, fibre, protein, salt = nutritional_values
            product_details['energy_kj'] = float(energy_kj)
            product_details['energy_kcal'] = float(energy_kcal)
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

    def assign_default_values(self, allergens):
        log.info(f"Assigning default values")
        product_details = {'energy_kj': 0.0, 'energy_kcal': 0.0, 'fat': 0.0, 'of_which_saturates': 0.0,
                           'carbohydrates': 0.0, 'of_which_sugars': 0.0, 'fibre': 0.0, 'protein': 0.0, 'salt': 0.0,
                           'allergens': allergens}
        return product_details

    def format_product_image_src(self, src):

        char_to_replace = "\\"
        return src.replace(char_to_replace, "/")

    def format_product_price_pence(self, price_string):
        char_to_remove = "p"
        price_string = price_string.replace(char_to_remove, "")
        return float(price_string)

    def format_product_price_pound(self, price_string):
        char_to_remove = "£"
        price_string = price_string.replace(char_to_remove, "")
        return float(price_string)

    def format_supermarket_category_products(self, product_list):
        for product in product_list:
            product.update({'image': self.format_product_image_src(product['image'])})
        return product_list

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

    def get_id(self):
        try:
            supermarket_object = db.get_table_object("supermarkets")
            row = db.session.query(supermarket_object).filter_by(supermarket_name=self.name).first()
            if row:
                return row.id
            else:
                return None
        except Exception as e:
            log.error(f"Error retrieving ID for {self.name}: {e}")
            return None

    def get_categories(self):
        try:
            supermarket_id = self.get_id()
            if supermarket_id is not None:
                supermarket_categories_object = db.get_table_object("supermarket_categories")
                return db.session.query(supermarket_categories_object).filter_by(supermarket_id=supermarket_id).all()
            else:
                log.warning("Supermarket ID not found")
                return []
        except Exception as e:
            log.exception(f"Error retrieving categories for {self.name}: {e}")
            return []

    def get_category_information(self, category_name):
        try:
            supermarket_categories_object = db.get_table_object("supermarket_categories")
            row = db.session.query(supermarket_categories_object).filter_by(
                supermarket_category_name=category_name).first()
            if row:
                category_id = row.id
                category_part_url = row.supermarket_category_part_url
                return category_id, category_part_url
            else:
                log.warning(f"{category_name} category not found")
                return None, None
        except Exception as e:
            log.exception(f"Error retrieving category information for '{category_name}': {e}")
            return None, None

    def get_allergens(self):
        return [
            "peanuts", "almonds", "walnuts", "cashews", "pistachios", "milk", "eggs", "wheat", "barley", "soy",
            "mustard", "lupin", "rye", "sulphites", "fish", "shellfish", "celery", "sesame", "molluscs"
        ]

    def get_nutrition_pattern(self):
        return r""

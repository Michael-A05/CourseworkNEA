import logging
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
        log.info(f"{self.name} loaded")

    def build_url(self, url, page):
        return ""

    def filter_categories(self, html):
        return []

    def filter_products(self, html):
        return []

    def filter_product_details(self, html):
        return {}

    def get_id(self):
        supermarket_object = db.get_table_object("supermarkets")
        row = db.session.query(supermarket_object).filter_by(supermarket_name=self.name).first()
        if row:
            return row.id
        else:
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
            log.exception(f"Error retrieving categories: {e}")
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
                log.warning(f"Category '{category_name}' not found")
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
        return (r"(Fat|of which saturates|Carbohydrate|of which sugars|Fibre|Protein|Salt)(\s+[<]?\d+[.]?\d+|\s+\d+)|("
                r"\d+kJ|\d+kcal)")

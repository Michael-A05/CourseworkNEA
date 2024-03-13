from database import Database
db = Database()


class Supermarkets():
    def __init__(self):
        self.name = ""
        self.logo = ""
        self.base_url = ""
        self.id = None
        self.categories = self.get_categories()

    def build_url(self, url, page):
        return ""

    def filter_categories(self, html):
        return []

    def filter_products(self, html):
        return []

    def get_id(self):
        supermarket_object = db.get_table_object("supermarkets")
        row = db.session.query(supermarket_object).filter_by(supermarket_name=self.name).first()
        if row:
            return row.id
        else:
            return None

    def get_categories(self):
        supermarket_categories_object = db.get_table_object("supermarket_categories")
        return db.session.query(supermarket_categories_object).filter_by(supermarket_id=self.get_id()).all()

    def get_category_information(self, category_name):
        supermarket_categories_object = db.get_table_object("supermarket_categories")
        row = db.session.query(supermarket_categories_object).filter_by(supermarket_category_name=category_name).first()
        category_id = row.id
        category_part_url = row.supermarket_category_part_url
        return category_id, category_part_url
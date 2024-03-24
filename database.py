import logging
from datetime import datetime

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

log = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class Supermarkets(Base):
    __tablename__ = "supermarkets"

    id: Mapped[int] = mapped_column(primary_key=True)
    supermarket_name: Mapped[str]
    supermarket_logo: Mapped[str]
    supermarket_base_url: Mapped[str]


class SupermarketCategories(Base):
    __tablename__ = "supermarket_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    supermarket_id: Mapped[int] = mapped_column(db.ForeignKey('supermarkets.id'))
    supermarket_category_name: Mapped[str]
    supermarket_category_part_url: Mapped[str]


class SupermarketProducts(Base):
    __tablename__ = "supermarket_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    supermarket_category_id: Mapped[int] = mapped_column(db.ForeignKey('supermarket_categories.id'))
    product_name: Mapped[str]
    product_price: Mapped[float]
    product_image: Mapped[str]
    product_part_url: Mapped[str]
    created: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    last_updated: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    is_available: Mapped[bool]


class SupermarketProductDetails(Base):
    __tablename__ = "supermarket_product_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    supermarket_product_id: Mapped[int] = mapped_column(db.ForeignKey('supermarket_products.id'))
    energy_kj: Mapped[float]
    energy_kcal: Mapped[float]
    fat: Mapped[float]
    of_which_saturates: Mapped[float]
    carbohydrates: Mapped[float]
    of_which_sugars: Mapped[float]
    fibre: Mapped[float]
    protein: Mapped[float]
    salt: Mapped[float]


class SupermarketProductAllergens(Base):
    __tablename__ = "supermarket_product_allergens"

    id: Mapped[int] = mapped_column(primary_key=True)
    supermarket_product_id: Mapped[int] = mapped_column(db.ForeignKey('supermarket_products.id'))
    allergen: Mapped[str]


class Database:
    def __init__(self):
        self.engine = db.create_engine(
            "sqlite:///supermarketscrape.db?check_same_thread=false"
        )
        log.info(f"Database loaded")

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.Base = declarative_base()

        class Supermarkets(self.Base):
            __tablename__ = "supermarkets"

            id = db.Column(db.Integer, primary_key=True)
            supermarket_name = db.Column(db.String)
            supermarket_logo = db.Column(db.String)
            supermarket_base_url = db.Column(db.String)

        class SupermarketCategories(self.Base):
            __tablename__ = "supermarket_categories"

            id = db.Column(db.Integer, primary_key=True)
            supermarket_id = db.Column(db.Integer, db.ForeignKey('supermarkets.id'))
            supermarket_category_name = db.Column(db.String)
            supermarket_category_part_url = db.Column(db.String)

        class SupermarketProducts(self.Base):
            __tablename__ = "supermarket_products"

            id = db.Column(db.Integer, primary_key=True)
            supermarket_category_id = db.Column(db.Integer, db.ForeignKey('supermarket_categories.id'))
            product_name = db.Column(db.String)
            product_price = db.Column(db.Float)
            product_image = db.Column(db.String)
            product_part_url = db.Column(db.String)
            created = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
            last_updated = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
            is_available = db.Column(db.Boolean)

        class SupermarketProductDetails(self.Base):
            __tablename__ = "supermarket_product_details"

            id = db.Column(db.Integer, primary_key=True)
            supermarket_product_id = db.Column(db.Integer, db.ForeignKey('supermarket_products.id'))
            energy_kj = db.Column(db.Float)
            energy_kcal = db.Column(db.Float)
            fat = db.Column(db.Float)
            of_which_saturates = db.Column(db.Float)
            carbohydrates = db.Column(db.Float)
            of_which_sugars = db.Column(db.Float)
            fibre = db.Column(db.Float)
            protein = db.Column(db.Float)
            salt = db.Column(db.Float)

        class SupermarketProductAllergens(self.Base):
            __tablename__ = "supermarket_product_allergens"

            id = db.Column(db.Integer, primary_key=True)
            supermarket_product_id = db.Column(db.Integer, db.ForeignKey('supermarket_products.id'))
            allergen = db.Column(db.String)

        self.Base.metadata.create_all(self.engine)
        log.info("Database tables loaded")

    def get_table_object(self, table_name):
        self.Base.metadata.reflect(self.engine)
        return self.Base.metadata.tables.get(table_name)

    def add_supermarket(self, supermarkets):
        supermarkets_table = self.get_table_object(table_name="supermarkets")

        with self.session as session:
            for supermarket in supermarkets:
                exists = (
                    self.session.query(supermarkets_table).filter_by(supermarket_name=supermarket.name).first()
                )
                if exists is None:
                    log.info(f"Adding {supermarket.name} to the 'Supermarkets' table")
                    supermarket = Supermarkets(
                        supermarket_name=supermarket.name,
                        supermarket_logo=supermarket.logo,
                        supermarket_base_url=supermarket.base_url
                    )
                    session.add(instance=supermarket)
                else:
                    log.warning(f"{supermarket.name} is already in the table")

            self.session.commit()

    def add_supermarket_category(self, data):
        categories_table = self.get_table_object(table_name="supermarket_categories")

        with self.session as session:
            for datum in data["supermarket_categories"]:
                exists = (
                    self.session.query(categories_table).filter_by(supermarket_category_name=datum['name']).first()
                )
                if exists is None:
                    log.info(f"Adding {datum['name']} to 'Super market categories'")
                    supermarket_category = SupermarketCategories(
                        supermarket_id=data["supermarket_id"],
                        supermarket_category_name=datum['name'],
                        supermarket_category_part_url=datum['part_url']
                    )
                    session.add(instance=supermarket_category)
                else:
                    log.info(f"{datum['name']} is already in the table")

            self.session.commit()

    def add_supermarket_category_products(self, data):  # add update_necessary_checking
        statistics = {"New": 0, "Updated": 0, "Deleted": 0}
        products_table = self.get_table_object("supermarket_products")

        #  check = (
        #      self.session.query(table_object).filter_by().all()
        #  )
        with self.session as session:
            for datum in data["supermarket_category_products"]:
                log.info(f"Adding {datum['name']}")
                statistics["New"] += 1
                product = SupermarketProducts(
                    supermarket_category_id=data["supermarket_category_id"],
                    product_name=datum['name'],
                    product_price=datum['price'],
                    product_image=datum['image'],
                    product_part_url=datum['part_url']
                )
                session.add(instance=product)

            self.session.commit()

    def add_product_information(self, data):

        with self.session as session:
            datum = data["supermarket_product_details"]
            supermarket_product_details = SupermarketProductDetails(
                supermarket_product_id=data["supermarket_product_id"],
                energy_kj=datum['energy_kj'],
                energy_kcal=datum['energy_kcal'],
                fat=datum['fat'],
                of_which_saturates=datum['of_which_saturates'],
                carbohydrates=datum['carbohydrates'],
                of_which_sugars=datum['of_which_sugars'],
                fibre=datum['fibre'],
                protein=datum['protein'],
                salt=datum['salt']
            )
            session.add(instance=supermarket_product_details)
            self.session.commit()

    def add_product_allergy_information(self, data):

        with self.session as session:
            datum = data["supermarket_product_details"]
            for allergen in datum['allergens']:
                supermarket_product_allergen = SupermarketProductAllergens(
                    supermarket_product_id=data["supermarket_product_id"],
                    allergen=allergen
                )
                session.add(instance=supermarket_product_allergen)
            self.session.commit()

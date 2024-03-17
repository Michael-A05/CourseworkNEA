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

    def filter_details(self, html):
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
                product_details['energy_kj'] = float(energy_kj)
                product_details['energy_kcal'] = float(energy_kcal)
                product_details['fat'] = float(fat)
                product_details['of_which_saturates'] = float(sat_fat)
                product_details['carbohydrates'] = float(carb)
                product_details['of_which_sugars'] = float(sugars)
                product_details['fibre'] = float(fibre)
                product_details['protein'] = float(protein)
                product_details['salt'] = float(salt)

        return product_details

    """
    def return_product_names(self, html):
        soup = BeautifulSoup(html, "html.parser")
        product_names = []

        for divtag in soup.find_all('div', {'class': 'product-tile'}):
            for product_name in divtag.find('a', {'class': 'p text-default-font'}):
                product_names.append(product_name)

        return product_names

    def return_product_prices(self, html):
        soup = BeautifulSoup(html, "html.parser")
        product_prices = []

        for divtag in soup.find_all('div', {'class': 'product-tile'}):
            for product_price in divtag.find('span', {'class': 'h4'}):
                product_price_string = product_price.string
                product_price = self.format_product_price(product_price_string)
                product_prices.append(product_price)

        return product_prices

    def return_product_part_urls(self, html):
        soup = BeautifulSoup(html, "html.parser")
        product_part_urls = []

        for divtag in soup.find_all('div', {'class': 'product-tile'}):
            for product_part_url in divtag.find('div', 'image-tile'):
                try:
                    product_part_url = product_part_url.get('href')
                    if product_part_url is not None:
                        product_part_urls.append(product_part_url)
                except AttributeError:
                    pass

        return product_part_urls
    
    
    def return_product_images(self, html):
        soup = BeautifulSoup(html, "html.parser")
        product_images = []

        for divtag in soup.find_all('div', {'class': 'product-tile'}):
            for product_image in divtag.find('figure'):
                product_image_src = product_image.get('src')
                product_images.append(product_image_src)

        return [self.format_product_image_src(product_image_src) for product_image_src in product_images]
    """

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

    """
    def convert_ingredients_text(self, ingredients_text):
        ingredients_text = ingredients_text.lower()
        ingredients_text = ingredients_text.strip()
        ingredients_list = ingredients_text.split(",")

        return [ingredient.lstrip() for ingredient in ingredients_list]

    def format_ingredients_list(self, ingredients_list):
        formatted_ingredients_list = []
        brackets = ["(", ")"]
        for ingredient in ingredients_list:
            formatted_ingredient = ""
            for letter in ingredient:
                if letter in brackets:
                    continue
                else:
                    formatted_ingredient += letter
            formatted_ingredients_list.append(formatted_ingredient)

        return formatted_ingredients_list

    def find_allergens(self, ingredients_list):
        ingredient_allergens = []
        allergens = self.get_allergens()
        false = -1
        for allergen in allergens:
            for ingredient in ingredients_list:
                contains_allergen = ingredient.find(allergen)
                if contains_allergen != false:
                    ingredient_allergens.append(allergen)

        return ingredient_allergens
    """


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

# aldi = Aldi()
# url = "https://groceries.aldi.co.uk/en-GB/bakery?&page=7"
# scraper = Scraper(aldi, database=None)
# html = scraper.get_html(url)
# x = aldi.return_product_images(html)
# print(x)

# y = ['https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\31.01.24\\4061459897302_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/$Aldi_GB/29.01.24/4061459984118_0.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\08.02.24\\4061464813496_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/image_not_found.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\01.03.24\\4088600554334_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\25.05.23\\4088600011899_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\4061464945791_db4552ab39a14cd8a831fa7c6840b558_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\4061464945951_39acea7de61144a1a9a83e6dc00a3a63_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\4061464945944_497bb9fe0de1437cacc583b11d315d45_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\25.05.23\\4088600229928_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/image_not_found.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\12.10.21(3)\\4088600338743_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\12.07.23\\4088600003610_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\27.04.23\\4088600276250_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/$Aldi_GB/26.07.22/4088600492605_0.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\27.04.23\\4088600276267_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\18.05.23\\5010044010137_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/$Aldi_GB/12.03.24/5027870206146_0.jpg', 'https://aldprdproductimages.azureedge.net/media/$Aldi_GB/09.02.23/4088600294964_0.jpg', 'https://aldprdproductimages.azureedge.net/media/$Aldi_GB/09.02.23/4088600294971_0.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\26.05.23\\4088600327587_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221606406_ef13e6e2ebe6448088652af3cca564a5_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\21.03.23\\4088600556055_0_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221603665_80ccf4ee6a234e92ab7bedb2f2e4a235_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221606970_1de4c59745e44366b467d3a153176b2e_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221608813_ded8cd3b57cb4c32bca15c6986208831_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5088722227085_176ab310200b48af9fb926d3b2647837_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5088722226064_d9e715d2c3f9437595a71334e2fd536c_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221602552_80ab431bb205464d9bfeddd3acee2edc_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221602606_47407f60ce6a4bfda7662f0ba4beb387_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221607946_e9d9c00d71164688a023021e7e917b72_M.jpg', 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221607953_b327cbed20304265a9be8cd911e03169_M.jpg']
# z = aldi.format_product_image_src(y[0])
# print(z)

# h = [aldi.format_product_image_src(x) for x in y]
# print(h)

# aldi = Aldi()
# pricestring = "£3.99"
# price = aldi.format_product_price(pricestring)
# print(price)

# aldi = Aldi()
# url = "https://groceries.aldi.co.uk/en-GB/bakery?&page=3"
# scraper = Scraper(aldi, database=None)
# html = scraper.get_html(url)
# supermarket_category_products = aldi.filter_products(html)
# print(supermarket_category_products)

# aldi = Aldi()
# testlist = [{'name': ' Specially Selected Mini Winter Dessert Cupcake Selectio ', 'price': 2.19, 'part_url': '/en-GB/p-specially-selected-mini-winter-dessert-cupcake-selection-198g9-pack/4061459897302', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\31.01.24\\4061459897302_0_M.jpg'}, {'name': ' Specially Selected Luxury Fruited Hot Cross Buns 260g/4 ', 'price': 1.25, 'part_url': '/en-GB/p-specially-selected-luxury-fruited-hot-cross-buns-260g4-pack/4061459984118', 'image': 'https://aldprdproductimages.azureedge.net/media/$Aldi_GB/29.01.24/4061459984118_0.jpg'}, {'name': ' Village Bakery High Protein Banana Pancakes 200g/4 Pack ', 'price': 1.29, 'part_url': '/en-GB/p-village-bakery-high-protein-banana-pancakes-200g4-pack/4061464813496', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\08.02.24\\4061464813496_0_M.jpg'}, {'name': ' Dairyfine Mini Chocolate Egg Cookies 4 Pack ', 'price': 1.39, 'part_url': '/en-GB/p-dairyfine-mini-chocolate-egg-cookies-4-pack/4061461510787', 'image': 'https://aldprdproductimages.azureedge.net/media/image_not_found.jpg'}, {'name': ' Village Bakery Caramelised Biscuit Flavoured Hot Cross  ', 'price': 1.25, 'part_url': '/en-GB/p-village-bakery-caramelised-biscuit-flavoured-hot-cross-buns-260g4-pack/4088600554334', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\01.03.24\\4088600554334_0_M.jpg'}, {'name': ' Village Bakery Bake At Home White Rolls 300g/4 Pack ', 'price': 0.79, 'part_url': '/en-GB/p-village-bakery-bake-at-home-white-rolls-300g4-pack/4088600011899', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\25.05.23\\4088600011899_0_M.jpg'}, {'name': ' Specially Selected Banoffee Hot Cross Buns 280g/4 Pack ', 'price': 1.25, 'part_url': '/en-GB/p-specially-selected-banoffee-hot-cross-buns-280g4-pack/4061464945791', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\4061464945791_db4552ab39a14cd8a831fa7c6840b558_M.jpg'}, {'name': ' Village Bakery Nutoka Hot Cross Buns 260g/4 Pack ', 'price': 1.25, 'part_url': '/en-GB/p-village-bakery-nutoka-hot-cross-buns-260g4-pack/4061464945951', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\4061464945951_39acea7de61144a1a9a83e6dc00a3a63_M.jpg'}, {'name': ' Specially Selected White Chocolate & Raspberry Hot Cros ', 'price': 1.25, 'part_url': '/en-GB/p-specially-selected-white-chocolate-raspberry-hot-cross-buns-280g4-pack/4061464945944', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\4061464945944_497bb9fe0de1437cacc583b11d315d45_M.jpg'}, {'name': ' Village Bakery Bake At Home White Baguettes 300g/2 Pack ', 'price': 0.79, 'part_url': '/en-GB/p-village-bakery-bake-at-home-white-baguettes-300g2-pack/4088600229928', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\25.05.23\\4088600229928_0_M.jpg'}, {'name': ' Holly Lane Vanilla Flavour Sponge Party Cakes 345g/12 P ', 'price': 1.89, 'part_url': '/en-GB/p-holly-lane-vanilla-flavour-sponge-party-cakes-345g12-pack/4088600551043', 'image': 'https://aldprdproductimages.azureedge.net/media/image_not_found.jpg'}, {'name': ' Holly Lane Cupcake Party Platter 636g/12 Pack ', 'price': 4.99, 'part_url': '/en-GB/p-holly-lane-cupcake-party-platter-636g12-pack/4088600338743', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\12.10.21(3)\\4088600338743_0_M.jpg'}, {'name': ' Inspired Cuisine Ciabatta Rolls 360g/4 Pack ', 'price': 1.15, 'part_url': '/en-GB/p-inspired-cuisine-ciabatta-rolls-360g4-pack/4088600003610', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\12.07.23\\4088600003610_0_M.jpg'}, {'name': ' Village Bakery Soft White Pittas 360g/6 Pack ', 'price': 0.5, 'part_url': '/en-GB/p-village-bakery-soft-white-pittas-360g6-pack/4088600276250', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\27.04.23\\4088600276250_0_M.jpg'}, {'name': ' Village Bakery Plain Flame Baked Folded Flatbreads 4x85 ', 'price': 0.99, 'part_url': '/en-GB/p-village-bakery-plain-flame-baked-folded-flatbreads-4x85g/4088600492605', 'image': 'https://aldprdproductimages.azureedge.net/media/$Aldi_GB/26.07.22/4088600492605_0.jpg'}, {'name': ' Village Bakery Wholemeal Pittas 360g/6 Pack ', 'price': 0.5, 'part_url': '/en-GB/p-village-bakery-wholemeal-pittas-360g6-pack/4088600276267', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\27.04.23\\4088600276267_0_M.jpg'}, {'name': ' Warburtons 4 White Soft Pittas 4 Pack ', 'price': 1.15, 'part_url': '/en-GB/p-warburtons-4-white-soft-pittas-4-pack/5010044010137', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\18.05.23\\5010044010137_0_M.jpg'}, {'name': ' Holly Lane Oat Flapjack 80g ', 'price': 0.69, 'part_url': '/en-GB/p-holly-lane-oat-flapjack-80g/5027870206146', 'image': 'https://aldprdproductimages.azureedge.net/media/$Aldi_GB/12.03.24/5027870206146_0.jpg'}, {'name': ' Village Bakery Bake At Home White Dinner Rolls 560g/8 P ', 'price': 1.89, 'part_url': '/en-GB/p-village-bakery-bake-at-home-white-dinner-rolls-560g8-pack/4088600294964', 'image': 'https://aldprdproductimages.azureedge.net/media/$Aldi_GB/09.02.23/4088600294964_0.jpg'}, {'name': ' Specially Selected Dark Rye Sourdough Loaf 500g ', 'price': 1.59, 'part_url': '/en-GB/p-specially-selected-dark-rye-sourdough-loaf-500g/4088600327587', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\26.05.23\\4088600327587_0_M.jpg'}, {'name': ' Village Bakery Bake At Home Seeded Dinner Rolls 560g/8  ', 'price': 1.89, 'part_url': '/en-GB/p-village-bakery-bake-at-home-seeded-dinner-rolls-560g8-pack/4088600294971', 'image': 'https://aldprdproductimages.azureedge.net/media/$Aldi_GB/09.02.23/4088600294971_0.jpg'}, {'name': ' Mr Kipling Fancies ', 'price': 1.99, 'part_url': '/en-GB/p-mr-kipling-fancies/5000221606406', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221606406_ef13e6e2ebe6448088652af3cca564a5_M.jpg'}, {'name': ' Village Bakery Jaffa Flavoured Hot Cross Buns 390g/6 Pa ', 'price': 1.29, 'part_url': '/en-GB/p-village-bakery-jaffa-flavoured-hot-cross-buns-390g6-pack/4088600556055', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\21.03.23\\4088600556055_0_M.jpg'}, {'name': ' Cadbury 4 Mini Eggs Nest Cakes 4 X Nest Cakes ', 'price': 2.49, 'part_url': '/en-GB/p-cadbury-4-mini-eggs-nest-cakes-4-x-nest-cakes/5000221603665', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221603665_80ccf4ee6a234e92ab7bedb2f2e4a235_M.jpg'}, {'name': ' Mr Kipling 5 Lemon & Raspberry Mini Batts 5 Pack ', 'price': 1.49, 'part_url': '/en-GB/p-mr-kipling-5-lemon-raspberry-mini-batts-5-pack/5000221606970', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221606970_1de4c59745e44366b467d3a153176b2e_M.jpg'}, {'name': ' Cadbury 6 Mini Eggs Choc Cakes 6 X Chock Cakes ', 'price': 2.49, 'part_url': '/en-GB/p-cadbury-6-mini-eggs-choc-cakes-6-x-chock-cakes/5000221608813', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221608813_ded8cd3b57cb4c32bca15c6986208831_M.jpg'}, {'name': ' Soreen 5 Lemon Mini Loaves 150g ', 'price': 1.25, 'part_url': '/en-GB/p-soreen-5-lemon-mini-loaves-150g/5088722227085', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5088722227085_176ab310200b48af9fb926d3b2647837_M.jpg'}, {'name': ' Soreen 5 Raspberry & White Chocolate Mini Loaves 150g ', 'price': 1.25, 'part_url': '/en-GB/p-soreen-5-raspberry-white-chocolate-mini-loaves-150g/5088722226064', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5088722226064_d9e715d2c3f9437595a71334e2fd536c_M.jpg'}, {'name': ' Cadbury 10 Mini Rolls Raspberry Family Size 10 X Mini R ', 'price': 2.39, 'part_url': '/en-GB/p-cadbury-10-mini-rolls-raspberry-family-size-10-x-mini-rolls/5000221602552', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221602552_80ab431bb205464d9bfeddd3acee2edc_M.jpg'}, {'name': ' Cadbury 10 Mini Rolls Milk Chocolate Family Size 10 X M ', 'price': 2.39, 'part_url': '/en-GB/p-cadbury-10-mini-rolls-milk-chocolate-family-size-10-x-mini-rolls/5000221602606', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221602606_47407f60ce6a4bfda7662f0ba4beb387_M.jpg'}, {'name': ' Mr Kipling 10 Gooey Brownie Bites Double Chocolate 10 P ', 'price': 1.25, 'part_url': '/en-GB/p-mr-kipling-10-gooey-brownie-bites-double-chocolate-10-pack/5000221607946', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221607946_e9d9c00d71164688a023021e7e917b72_M.jpg'}, {'name': ' Mr Kipling 10 Gooey Brownie Bites Salted Caramel 10 Pac ', 'price': 1.25, 'part_url': '/en-GB/p-mr-kipling-10-gooey-brownie-bites-salted-caramel-10-pack/5000221607953', 'image': 'https://aldprdproductimages.azureedge.net/media/resized\\$Aldi_GB\\5000221607953_b327cbed20304265a9be8cd911e03169_M.jpg'}]
# for data in testlist:
#    image_src = aldi.format_product_image_src(data['image'])
#    data.update({'image': image_src})
# print(testlist)

"""
aldi = Aldi()
url = "https://groceries.aldi.co.uk/en-GB/p-village-bakery-toastie-thick-sliced-white-bread-800g/4088600253305"
scraper = Scraper(aldi, database=None)
html = scraper.get_html(url)
aldi.filter_details(html)
"""
# testing = ['𝐖𝐡𝐞𝐚𝐭 𝐅𝐥𝐨𝐮𝐫 (𝐖𝐡𝐞𝐚𝐭 𝐅𝐥𝐨𝐮𝐫', 'calcium carbonate', 'iron', 'niacin', 'thiamin)', 'water', 'salt', 'yeast', '𝐒𝐨𝐲𝐚 flour', 'preservative: calcium propionate; emulsifier: mono- and diacetyl tartaric acid esters of mono- and diglycerides of fatty acids; spirit vinegar', 'rapeseed oil', 'flour treatment agent: ascorbic acid.']
# test = []
# allergens = "𝐖𝐡𝐞𝐚𝐭 𝐅𝐥𝐨𝐮𝐫 𝐒𝐨𝐲𝐚"
# print(type(allergens))

# x = str(allergens).find("Wheat")
# print(x)
# ingredient_allergies = []

# for string in testing:
#   brackets = ["(", ")"]
#   newstring = ""
#   for char in string:
#       if char in brackets:
#           continue
#       else:
#           newstring += char
#   test.append(newstring)

# print(test)

# for allergen in allergens:
#    for ingredient in test:
#        found = ingredient.find(allergen)
#        if found != -1:
#            ingredient_allergies.append(allergen)

# print(ingredient_allergies)

#teststring = "Per 100g:Energy 1009kJ, 239kcalFat 2.0gof which saturates 0.5gCarbohydrate 45gof which sugars 2.9gFibre 3.6gProtein 8.3gSalt 0.87g"
#pattern = r"(\d+kJ|\d+kcal)|Fat\s+([\d]+\.\d+g)|which saturates\s+([\d]+\.\d+g)|Carbohydrate\s+([\d]+\.*\d+g)|which sugars\s+([\d]+\.\d+g)|Fibre\s+([\d]+\.\d+g)|Protein\s+([\d]+\.\d+g)|Salt\s+([\d]+\.\d+g)"

#match = re.match(pattern, teststring)
"\d+(?:kJ|kcal)"
"Fat\s+([\d]+.[\d]g)"
"Saturated Fat\s+([\d]+.[\d]g)"
"Carbohydrate\s+([\d]+.[\d]g)"
"which Sugars\s+([\d]+.[\d]g)"
"Fibres\s+([\d]+.[\d]g)"
"Protein\s+([\d]+.[\d]g)"
"Salt\s+([\d]+.[\d]g)"

"""
nutritional_info = ("Per 100g:Energy 1009kJ, 239kcalFat 2.0gof which saturates 0.5gCarbohydrate 45gof which sugars "
                    "2.9gFibre 3.6gProtein 8.3gSalt 0.87g")

pattern = (r'Energy\s+(\d+kJ),\s+(\d+kcal)Fat\s+([\d.]+)gof which saturates\s+([\d.]+)gCarbohydrate\s+([\d.]+)gof '
           r'which sugars\s+([\d.]+)gFibre\s+([\d.]+)gProtein\s+([\d.]+)gSalt\s+([\d.]+)g')

match = re.search(pattern, nutritional_info)

if match:
    energy_kj = match.group(1)
    energy_kcal = match.group(2)
    fat_g = match.group(3)
    saturates_g = match.group(4)
    carb_g = match.group(5)
    sugars_g = match.group(6)
    fibre_g = match.group(7)
    protein_g = match.group(8)
    salt_g = match.group(9)

    print(f"Energy: {energy_kj} kJ, {energy_kcal} kcal")
    print(f"Fat: {fat_g}g (of which saturates: {saturates_g}g)")
    print(f"Carbohydrate: {carb_g}g (of which sugars: {sugars_g}g)")
    print(f"Fibre: {fibre_g}g")
    print(f"Protein: {protein_g}g")
    print(f"Salt: {salt_g}g")
else:
    print("No match found.")
"""
"""
#error here
nutritional_info = ("Per 100g:Energy 1009kJ, 239kcalFat 2.0gof which saturates 0.5gCarbohydrate 45gof which sugars "
                    "2.9gFibre 3.6gProtein 8.3gSalt 0.87g")
pattern = "(\d+kJ|\d+kcal)|Fat\s+([\d]+\.\d+g)|which saturates\s+([\d]+\.\d+g)|Carbohydrate\s+([\d]+\.*\d+g)|which sugars\s+([\d]+\.\d+g)|Fibre\s+([\d]+\.\d+g)|Protein\s+([\d]+\.\d+g)|Salt\s+([\d]+\.\d+g)"
matches = re.findall(pattern, nutritional_info)
print(matches)
"""

nutritional_info = ("Per 100g:Energy 1009kJ, 239kcalFat 2.0gof which saturates 0.5gCarbohydrate 45gof which sugars "
                    "2.9gFibre 3.6gProtein 8.3gSalt 0.87g")

pattern = (r'Energy\s+(\d+kJ),\s+(\d+kcal)Fat\s+([\d.]+)gof which saturates\s+([\d.]+)gCarbohydrate\s+([\d.]+)gof '
           r'which sugars\s+([\d.]+)gFibre\s+([\d.]+)gProtein\s+([\d.]+)gSalt\s+([\d.]+)g')

matches = re.findall(pattern, nutritional_info)
energy_kj, energy_kcal, fat, sat_fat, carb, sugars, fibre, protein, salt = matches[0]
energy = f"{energy_kj} kJ, {energy_kcal} kcal"
print(f"Energy: {energy}")
print(f"Fat: {fat}")
print(f"Saturated Fat: {sat_fat}")
print(f"Carbohydrate: {carb}")
print(f"of which sugars: {sugars}")
print(f"Fibre: {fibre}")
print(f"Protein: {protein}")
print(f"Salt: {salt}")

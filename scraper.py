import logging
import time

import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

log = logging.getLogger(__name__)


class Scraper:
    def __init__(self, supermarkets, database):
        self.supermarkets = supermarkets
        self.database = database

    def scrape(self):
        try:
            return self.scrape_cycle()
        except requests.exceptions.Timeout:
            log.warning("Request timed out")
        except requests.exceptions.TooManyRedirects:
            log.warning("Too many redirects")
        except requests.exceptions.RequestException as e:
            log.warning(f"Request except: {e}")
        return None

    def scrape_cycle(self):
        category_id_index = 0
        category_part_url_index = 1
        category_name_index = 2

        self.database.add_supermarket(self.supermarkets)

        for supermarket in self.supermarkets:
            log.info(f"Adding {supermarket.name} categories")
            html = self.get_html(url=supermarket.base_url)
            supermarket_categories = supermarket.filter_categories(html)
            self.database.add_supermarket_category(
                {"supermarket_id": supermarket.get_id(), "supermarket_categories": supermarket_categories}
            )

            categories = supermarket.get_categories()
            for category in categories:
                category_name = category[category_name_index]
                log.info(f"Retrieving {category_name} products")

                category_information = supermarket.get_category_information(category_name)
                start_page_url = supermarket.base_url + category_information[category_part_url_index]
                page = 1
                finished = False

                while not finished:
                    url = supermarket.build_url(url=start_page_url, page=page)
                    html = self.get_html(url=url)
                    if html is None:
                        finished = True
                    else:
                        supermarket_category_products = supermarket.filter_products(html)
                        if len(supermarket_category_products) == 0:
                            finished = True
                        else:
                            self.database.add_supermarket_category_products(
                                {"supermarket_category_id": category_information[category_id_index],
                                 "supermarket_category_products": supermarket_category_products}
                            )
                            # new code here
                            supermarket_products_object = self.database.get_table_object("supermarket_products")
                            products = self.database.session.query(supermarket_products_object).filter_by(supermarket_category_id=category_information[category_id_index]).all()
                            for product in products:
                                product_id, product_part_url = product.id, product.product_part_url

                                url = supermarket.base_url + product_part_url
                                html = self.get_html(url=url)
                                supermarket_product_details = supermarket.filter_product_details(html)
                                self.database.add_product_information(
                                    {"supermarket_product_id": product_id,
                                     "supermarket_product_details": supermarket_product_details
                                     }
                                )
                                self.database.add_product_allergy_information(
                                    {"supermarket_product_id": product_id,
                                     "supermarket_product_details": supermarket_product_details
                                     }
                                )
                            page += 1

    def get_html(self, url):
        log.info(f"Scraping {url}")
        user_agent = ("Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                      "Mobile/15E148")

        options = Options()
        options.add_argument("start-maximized")
        # options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument(f"user-agent={user_agent}")

        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
        except WebDriverException as e:
            log.error(f"Selenium exception: {e.msg}")
            return None

        time.sleep(5)
        html = driver.page_source
        driver.quit()
        return html

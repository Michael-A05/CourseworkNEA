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
        self.database.add_supermarket(self.supermarkets)

        for supermarket in self.supermarkets:
            log.info(f"Adding {supermarket.name} categories")
            html = self.get_html(url=supermarket.base_url)
            supermarket_categories = supermarket.filter_categories(html)
            self.database.add_supermarket_category({"supermarket": supermarket.name, "supermarket_categories": supermarket_categories})

    def get_html(self, url):
        log.info(f"Scraping {url}")
        user_agent = ("Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                      "Mobile/15E148")

        options = Options()
        options.add_argument("start-maximized")
        options.add_argument('--headless')
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
    
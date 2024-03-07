import logging
import os
from pathlib import Path
from aldi import Aldi
from scraper import Scraper
from database import Database


logs_file = Path(Path().resolve(), "log.text")
logs_file.touch(exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO"),
    handlers=[logging.FileHandler(logs_file), logging.StreamHandler()],
)

log = logging.getLogger(__name__)

db = Database()
supermarkets = [Aldi()]
scraper = Scraper(supermarkets=supermarkets, database=db)
scraper.scrape()
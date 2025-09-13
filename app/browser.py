from typing import Dict
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from . import utils


def create_driver(cfg: Dict) -> webdriver.Chrome:
    """Create a Selenium Chrome WebDriver based on config."""
    options = Options()
    if cfg.get("headless", True):
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    ua = cfg.get("user_agent") or utils.random_ua()
    options.add_argument(f"--user-agent={ua}")
    if cfg.get("use_proxy"):
        proxies = utils.load_proxies(cfg.get("proxy_file", "data/proxies.txt"))
        if proxies:
            proxy = random.choice(proxies)
            options.add_argument(f"--proxy-server={proxy}")
    driver = webdriver.Chrome(options=options)
    return driver

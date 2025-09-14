from __future__ import annotations

from typing import Dict
import random

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except ImportError as exc:  # pragma: no cover - handled at runtime
    webdriver = None
    Options = None
    _import_error = exc

from . import utils


def create_driver(cfg: Dict) -> webdriver.Chrome:
    """Create a Selenium Chrome WebDriver based on config."""
    if webdriver is None or Options is None:  # pragma: no cover - executed only if selenium missing
        raise ImportError("selenium is required. Install with `pip install selenium`.") from _import_error

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
    timeout = cfg.get("page_load_timeout", 30)
    driver.set_page_load_timeout(timeout)
    return driver

import re
from typing import Dict, List

from loguru import logger

from . import anti_block, parser, utils, storage

AUTHOR_ID_RE = re.compile(r"(\d+)$")


def extract_author_id(url: str) -> str:
    m = AUTHOR_ID_RE.search(url)
    return m.group(1) if m else url


def crawl_author(author_url: str, cfg: Dict, store: storage.Storage) -> List[parser.Article]:
    author_id = extract_author_id(author_url)
    session = anti_block.get_session(cfg.get("request", {}).get("headers"))
    resp = anti_block.request_with_retry(
        session,
        author_url,
        timeout=cfg.get("request", {}).get("timeout", 15),
        retry=cfg.get("request", {}).get("retry", 3),
        backoff=cfg.get("request", {}).get("backoff", 1.5),
        proxies=cfg.get("request", {}).get("proxies"),
    )
    links = parser.parse_article_list(resp.text)
    articles = []
    limit = cfg.get("throttle", {}).get("per_author_limit", 5)
    for url in links[:limit]:
        if store.article_exists(parser.ARTICLE_ID_RE.search(url).group(1)):
            logger.info("existing article detected, stop further fetching")
            break
        art_resp = anti_block.request_with_retry(
            session,
            url,
            timeout=cfg.get("request", {}).get("timeout", 15),
            retry=cfg.get("request", {}).get("retry", 3),
            backoff=cfg.get("request", {}).get("backoff", 1.5),
            proxies=cfg.get("request", {}).get("proxies"),
        )
        article = parser.parse_article(art_resp.text, url, author_id, author_id)
        articles.append(article)
        utils.random_delay(
            cfg.get("throttle", {}).get("min_delay", 1.0),
            cfg.get("throttle", {}).get("max_delay", 3.0),
        )
    return articles


def crawl_from_file(file_path: str, cfg: Dict) -> None:
    authors = utils.load_authors(file_path)
    store = storage.Storage(
        save_json=cfg.get("storage", {}).get("save_json", True),
        save_text=cfg.get("storage", {}).get("save_text", True),
        sqlite=cfg.get("storage", {}).get("sqlite", True),
    )
    for author_url in authors:
        try:
            arts = crawl_author(author_url, cfg, store)
            storage.save_articles(arts, store)
        except Exception as exc:  # noqa: BLE001
            logger.error(f"error crawling {author_url}: {exc}")
    store.close()

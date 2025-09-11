from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup


@dataclass
class Article:
    article_id: str
    url: str
    title: str
    author_id: str
    author_name: str
    publish_time: datetime
    content_html: str
    content_text: str
    images: List[str]


ARTICLE_ID_RE = re.compile(r"id=(\d+)")


def parse_article_list(html: str) -> List[str]:
    """Parse author page HTML to extract article URLs."""
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.select("a[href^='https://baijiahao.baidu.com/s?id=']"):
        links.append(a['href'])
    return links


def parse_article(html: str, url: str, author_id: str, author_name: str) -> Article:
    soup = BeautifulSoup(html, "lxml")
    title = soup.select_one("h1").get_text(strip=True)
    time_str = soup.select_one("time").get("datetime") if soup.select_one("time") else ""
    publish_time = datetime.fromisoformat(time_str) if time_str else datetime.utcnow()
    content_div = soup.select_one("div.content") or soup
    content_html = str(content_div)
    content_text = content_div.get_text("\n", strip=True)
    images = [img.get("src") or img.get("data-src") for img in content_div.find_all("img")]
    match = ARTICLE_ID_RE.search(url)
    article_id = match.group(1) if match else url
    return Article(
        article_id=article_id,
        url=url,
        title=title,
        author_id=author_id,
        author_name=author_name,
        publish_time=publish_time,
        content_html=content_html,
        content_text=content_text,
        images=images,
    )

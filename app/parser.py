from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import List

try:  # pragma: no cover - optional dependency
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover - fallback when bs4 is unavailable
    BeautifulSoup = None


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
    if BeautifulSoup:
        soup = BeautifulSoup(html, "lxml")
        return [
            a["href"]
            for a in soup.select("a[href^='https://baijiahao.baidu.com/s?id=']")
        ]
    return re.findall(r"https://baijiahao\.baidu\.com/s\?id=\d+", html)


def parse_article(html: str, url: str, author_id: str, author_name: str) -> Article:
    if BeautifulSoup:
        soup = BeautifulSoup(html, "lxml")
        title = soup.select_one("h1").get_text(strip=True)
        time_el = soup.select_one("time")
        time_str = time_el.get("datetime") if time_el else ""
        publish_time = (
            datetime.fromisoformat(time_str) if time_str else datetime.utcnow()
        )
        content_div = soup.select_one("div.content") or soup
        content_html = str(content_div)
        content_text = content_div.get_text("\n", strip=True)
        images = [
            img.get("src") or img.get("data-src")
            for img in content_div.find_all("img")
        ]
    else:  # fallback simple regex parsing
        title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
        title = title_match.group(1).strip() if title_match else ""
        time_match = re.search(r"<time[^>]*datetime=\"([^\"]+)\"", html)
        publish_time = (
            datetime.fromisoformat(time_match.group(1))
            if time_match
            else datetime.utcnow()
        )
        content_match = re.search(
            r"<div[^>]*class=['\"]content['\"][^>]*>(.*?)</div>", html, re.S
        )
        content_html = content_match.group(1) if content_match else ""
        content_text = re.sub(r"<[^>]+>", "", content_html)
        images = re.findall(r"<img[^>]*src=['\"]([^'\"]+)['\"]", content_html)
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

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:  # pragma: no cover - optional dependency
    from loguru import logger  # type: ignore
except Exception:  # pragma: no cover - fallback when loguru is missing
    import logging

    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

from .parser import Article

DB_PATH = Path("storage/baijiahao.db")


class Storage:
    def __init__(
        self,
        save_json: bool = True,
        save_text: bool = True,
        sqlite: bool = True,
        db_path: Path | None = None,
    ):
        self.save_json = save_json
        self.save_text = save_text
        self.sqlite_enabled = sqlite
        self.db_path = db_path or DB_PATH
        if sqlite:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self._init_db()
        else:
            self.conn = None

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                article_id TEXT PRIMARY KEY,
                url TEXT,
                title TEXT,
                author_id TEXT,
                author_name TEXT,
                publish_time TEXT,
                content_html TEXT,
                content_text TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        self.conn.commit()

    def article_exists(self, article_id: str) -> bool:
        if not self.sqlite_enabled:
            return False
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM articles WHERE article_id=?", (article_id,))
        return cur.fetchone() is not None

    def save_article(self, article: Article) -> None:
        if self.sqlite_enabled:
            now = datetime.utcnow().isoformat()
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT OR IGNORE INTO articles (
                    article_id, url, title, author_id, author_name, publish_time,
                    content_html, content_text, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    article.article_id,
                    article.url,
                    article.title,
                    article.author_id,
                    article.author_name,
                    article.publish_time.isoformat(),
                    article.content_html,
                    article.content_text,
                    now,
                    now,
                ),
            )
            self.conn.commit()
        if self.save_json or self.save_text:
            self._save_files(article)

    def _save_files(self, article: Article) -> None:
        date_dir = Path("output") / datetime.utcnow().strftime("%Y%m%d") / article.author_id
        date_dir.mkdir(parents=True, exist_ok=True)
        if self.save_json:
            json_path = date_dir / f"{article.article_id}.json"
            json_path.write_text(json.dumps(asdict(article), ensure_ascii=False, indent=2), encoding="utf-8")
        if self.save_text:
            txt_path = date_dir / f"{article.article_id}.txt"
            txt_path.write_text(article.content_text, encoding="utf-8")

    def close(self) -> None:
        if self.conn:
            self.conn.close()


def save_articles(articles: Iterable[Article], storage: Storage) -> None:
    for art in articles:
        if storage.article_exists(art.article_id):
            logger.info(f"skip existing article {art.article_id}")
            continue
        storage.save_article(art)

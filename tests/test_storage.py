from datetime import datetime

from app.parser import Article
from app.storage import Storage


def create_article(article_id: str) -> Article:
    return Article(
        article_id=article_id,
        url=f"https://example.com/{article_id}",
        title="t",
        author_id="a",
        author_name="a",
        publish_time=datetime.utcnow(),
        content_html="<p>hi</p>",
        content_text="hi",
        images=[],
    )


def test_sqlite_crud(tmp_path):
    db = tmp_path / "t.db"
    store = Storage(save_json=False, save_text=False, sqlite=True, db_path=db)
    art = create_article("1")
    store.save_article(art)
    assert store.article_exists("1")
    # dedup insert
    store.save_article(art)
    cur = store.conn.cursor()
    cur.execute("SELECT COUNT(*) FROM articles")
    count = cur.fetchone()[0]
    assert count == 1
    store.close()

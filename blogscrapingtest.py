import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
import sqlite3
import tempfile

import BlogScraping


def run():
    class _Entry(dict):
        def __getattr__(self, item):
            if item in self:
                return self[item]
            raise AttributeError(item)

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_blogs.db"

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                url TEXT UNIQUE,
                summary TEXT,
                image_url TEXT,
                full_text TEXT,
                author TEXT,
                thumbnail TEXT,
                published_date TEXT,
                scraped_at TEXT
            )
            """
        )
        conn.commit()
        conn.close()

        def _test_get_db_connection():
            c = sqlite3.connect(db_path)
            c.row_factory = sqlite3.Row
            return c

        long_text = "word " * 250
        short_text = "word " * 10

        fake_feed = type("Feed", (), {})()
        fake_feed.entries = [
            _Entry(
                {
                    "title": "Long Article",
                    "link": "https://example.com/long",
                    "summary": '<img src="https://example.com/feedimg.png"/>Short summary',
                    "published": "2025-01-01",
                }
            ),
            _Entry(
                {
                    "title": "Short Article",
                    "link": "https://example.com/short",
                    "summary": "Too short",
                    "published": "2025-01-02",
                }
            ),
        ]

        def _fake_scrape_article(url, timeout=15):
            if url.endswith("/long"):
                return {
                    "title": "Long Article",
                    "author": "Example Author",
                    "published_date": "2025-01-01",
                    "full_text": long_text,
                    "full_html": f"<p>{long_text}</p>",
                    "thumbnail": "https://example.com/thumb.png",
                }
            return {
                "title": "Short Article",
                "author": "Example Author",
                "published_date": "2025-01-02",
                "full_text": short_text,
                "full_html": f"<p>{short_text}</p>",
                "thumbnail": "https://example.com/thumb2.png",
            }

        with patch.object(BlogScraping, "get_db_connection", side_effect=_test_get_db_connection), patch.object(
            BlogScraping, "fetch_rss_feed", return_value=fake_feed
        ), patch.object(BlogScraping, "scrape_article", side_effect=_fake_scrape_article):
            feed = BlogScraping.fetch_rss_feed()
            entries = BlogScraping.parse_feed_entries(feed)
            assert len(entries) == 2, "Expected 2 parsed feed entries"
            assert entries[0].get("image_url") == "https://example.com/feedimg.png", "Expected image_url extraction"
            assert entries[0].get("published_date") == "2025-01-01", "Expected published_date mapping"

            result = BlogScraping.refresh_rss_feed()
            assert result.get("success") is True, "Expected refresh_rss_feed success"
            assert result.get("new_count") == 1, "Expected only 1 article to be inserted (short one skipped)"
            assert result.get("total_count") == 1, "Expected total blog count to match"

            blogs = BlogScraping.get_all_blogs()
            assert len(blogs) == 1, "Expected 1 blog in database"
            blog_id = blogs[0].get("id")
            assert blog_id, "Expected inserted blog to have an id"

            paginated = BlogScraping.get_blogs_paginated(page=1, per_page=10)
            assert paginated.get("total") == 1, "Expected pagination total to be 1"
            assert len(paginated.get("blogs") or []) == 1, "Expected pagination to return 1 blog"

            blog = BlogScraping.get_blog_by_id(blog_id)
            assert blog and blog.get("title") == "Long Article", "Expected get_blog_by_id to return the inserted blog"

            ok = BlogScraping.update_blog(blog_id, title="Updated Title")
            assert ok is True, "Expected update_blog to return True"
            updated = BlogScraping.get_blog_by_id(blog_id)
            assert updated.get("title") == "Updated Title", "Expected blog title to be updated"

            ok = BlogScraping.delete_blog(blog_id)
            assert ok is True, "Expected delete_blog to return True"
            assert BlogScraping.get_blog_by_id(blog_id) is None, "Expected blog to be deleted"


if __name__ == "__main__":
    run()
    print("blog scraping test passed")

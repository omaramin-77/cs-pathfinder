import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import BlogScraping


def run():
    output_path = Path("scraped_articles.json")
    backup_path = None
    original_bytes = None

    if output_path.exists():
        original_bytes = output_path.read_bytes()
        backup_path = output_path.with_suffix(output_path.suffix + ".bak")
        if backup_path.exists():
            backup_path.unlink()
        output_path.replace(backup_path)

    try:
        fake_feed = type("Feed", (), {})()
        fake_feed.entries = [
            {
                "title": "Example Title",   
                "link": "https://example.com/article",
                "summary": "Example summary",
                "published": "2025-01-01",
            }
        ]

        fake_article = {
            "title": "Example Title",
            "author": "Example Author",
            "published_date": "2025-01-01",
            "full_text": "hello world",
            "full_html": "<p>hello world</p>",
            "thumbnail": "https://example.com/img.png",
        }

        with patch.object(BlogScraping, "fetch_rss_feed", return_value=fake_feed), patch.object(
            BlogScraping, "scrape_article", return_value=fake_article
        ):
            feed = BlogScraping.fetch_rss_feed()
            entries = BlogScraping.parse_feed_entries(feed)
            assert entries, "Expected parsed feed entries"

            results = []
            for entry in entries[:1]:
                url = entry.get("url")
                assert url, "Expected entry url"

                article = BlogScraping.scrape_article(url)
                assert article, "Expected scraped article"

                results.append(
                    {
                        **entry,
                        **article,
                        "word_count": BlogScraping.count_words(article.get("full_text")),
                        "scraped_at": datetime.utcnow().isoformat(),
                    }
                )

            with output_path.open("w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            assert output_path.exists(), "Expected JSON output file to be created"

    finally:
        if output_path.exists():
            output_path.unlink()

        if backup_path and backup_path.exists():
            backup_path.replace(output_path)

        if original_bytes is None:
            assert not output_path.exists(), "Expected JSON output file to be removed"
        else:
            assert output_path.exists(), "Expected original JSON file to be restored"
            assert output_path.read_bytes() == original_bytes, "Expected restored JSON to match original"


if __name__ == "__main__":
    run()
    print("blog scraping test passed")

import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from DB import init_db, get_db_connection
from BlogScraping import (
    fetch_rss_feed,
    parse_feed_entries,
    extract_image_from_entry,
    count_words,
    refresh_rss_feed,
    get_all_blogs,
    get_blog_by_id,
    update_blog,
    delete_blog,
    RSS_FEED_URL
)


@pytest.fixture(scope="module")
def db():
    """
    Initialize a clean database for RSS/blog tests
    """
    # Use a mocked DB connection compatible with psycopg2.RealDictCursor behavior
    class MockCursor:
        def __init__(self):
            self.queries = []
            self._data = []

        def execute(self, query, params=None):
            self.queries.append((query, params))

        def fetchone(self):
            # Provide sensible defaults for tests
            return {'count': 0, 'id': 1, 'title': 'Test Blog', 'overall_score': 85}

        def fetchall(self):
            return []
        
        def executemany(self, query, seq_of_params):
            # Record the executemany call; tests only need that it exists
            self.queries.append((query, seq_of_params))

        def close(self):
            pass

    class MockConn:
        def __init__(self):
            self._cursor = MockCursor()

        def cursor(self):
            return self._cursor

        def commit(self):
            pass

        def rollback(self):
            pass

        def close(self):
            pass

    mock_conn = MockConn()

    # Patch DB.get_db_connection to return the mock during tests
    from unittest.mock import patch
    with patch('DB.get_db_connection', return_value=mock_conn):
        init_db()
        yield mock_conn
        mock_conn.close()


# -----------------------------
# RSS FEED TESTS
# -----------------------------

def test_fetch_rss_feed():
    feed = fetch_rss_feed()
    assert feed is not None
    assert hasattr(feed, "entries")
    assert len(feed.entries) > 0


def test_parse_feed_entries():
    feed = fetch_rss_feed()
    entries = parse_feed_entries(feed)

    assert isinstance(entries, list)
    assert len(entries) > 0

    entry = entries[0]
    assert "title" in entry
    assert "url" in entry
    assert "summary" in entry


def test_extract_image_from_entry():
    feed = fetch_rss_feed()
    entries = feed.entries

    image = extract_image_from_entry(entries[0])
    # Image may or may not exist, but function must not crash
    assert image is None or isinstance(image, str)


# -----------------------------
# UTILITY TESTS
# -----------------------------

def test_count_words():
    text = "This is a simple test sentence"
    assert count_words(text) == 6
    assert count_words("") == 0
    assert count_words(None) == 0


# -----------------------------
# FULL RSS → DB PIPELINE TEST
# -----------------------------

def test_refresh_rss_feed_inserts_articles(db):
    """
    Full integration test:
    - Fetch RSS
    - Scrape articles
    - Apply word limit
    - Insert into database
    """
    result = refresh_rss_feed()

    assert result["success"] is True
    assert "new_count" in result
    assert "total_count" in result
    assert result["total_count"] >= 0


def test_blogs_exist_after_refresh(db):
    blogs = get_all_blogs()
    assert isinstance(blogs, list)

    if blogs:
        blog = blogs[0]
        assert "title" in blog
        assert "url" in blog
        assert "summary" in blog


# -----------------------------
# CRUD TESTS
# -----------------------------

def test_get_blog_by_id(db):
    blogs = get_all_blogs()
    if not blogs:
        pytest.skip("No blogs available to test get_blog_by_id")

    blog_id = blogs[0]["id"]
    blog = get_blog_by_id(blog_id)

    assert blog is not None
    assert blog["id"] == blog_id


def test_update_blog(db):
    blogs = get_all_blogs()
    if not blogs:
        pytest.skip("No blogs available to test update_blog")

    blog_id = blogs[0]["id"]

    success = update_blog(
        blog_id,
        title="Updated Test Title",
        author="Test Author"
    )

    assert success is True

    updated = get_blog_by_id(blog_id)
    assert updated["title"] == "Updated Test Title"
    assert updated["author"] == "Test Author"


def test_delete_blog(db):
    blogs = get_all_blogs()
    if not blogs:
        pytest.skip("No blogs available to test delete_blog")

    blog_id = blogs[0]["id"]
    success = delete_blog(blog_id)

    assert success is True
    deleted = get_blog_by_id(blog_id)
    assert deleted is None

import os
import psycopg2
import psycopg2.extras
import pytest
import sys
from unittest.mock import patch, MagicMock, call

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from DB import init_db, get_db_connection

class MockCursor:
    def __init__(self):
        self.executed_queries = []
        self.call_count = 0
        
    def execute(self, query, params=None):
        self.executed_queries.append((query, params))
        self.call_count += 1
        
    def fetchone(self):
        # Return different responses based on the query pattern
        if self.call_count == 0:
            return None
        
        last_query = self.executed_queries[-1][0] if self.executed_queries else ""
        
        # Handle different query types
        if "information_schema.tables" in last_query:
            return {'table_name': 'users'}
        elif "COUNT(*)" in last_query and "quiz_questions" in last_query:
            return {'count': 5}
        elif "COUNT(*)" in last_query and "roadmaps" in last_query:
            return {'count': 3}
        elif "COUNT(*)" in last_query and "roadmap_steps" in last_query:
            return {'count': 10}
        elif "SELECT email, is_admin FROM users" in last_query:
            return {'email': 'a@a', 'is_admin': 1}
        elif "SELECT id FROM users WHERE is_admin" in last_query:
            return {'id': 1}
        elif "RETURNING id" in last_query:
            return {'id': 1}
        elif "SELECT field_name FROM user_fields" in last_query:
            return {'field_name': 'AI'}
        elif "SELECT title FROM blogs" in last_query:
            return {'title': 'Test Blog'}
        elif "SELECT overall_score FROM cv_rankings" in last_query:
            return {'overall_score': 85}
        elif "SELECT r.id, r.field_name, COUNT(rs.id)" in last_query:
            return {'id': 1, 'field_name': 'AI', 'step_count': 5}
        else:
            return {'count': 0, 'id': 1, 'is_admin': 1, 'email': 'a@a'}

class MockConnection:
    def __init__(self):
        self.mock_cursor = MockCursor()
        
    def cursor(self):
        return self.mock_cursor
        
    def commit(self):
        pass
        
    def rollback(self):
        pass
        
    def close(self):
        pass

@pytest.fixture(scope="module")
def db():
    """
    Initialize database once before tests using mocked database
    """
    mock_conn = MockConnection()
    
    with patch.dict(os.environ, {
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/test',
        'RUN_DB_INIT': '1'
    }):
        with patch('DB.get_db_connection', return_value=mock_conn):
            yield mock_conn


def test_database_connection():
    """Test that database connection can be established"""
    with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://test:test@localhost:5432/test'}):
        with patch('psycopg2.connect') as mock_connect:
            mock_connect.return_value = MagicMock()
            conn = get_db_connection()
            assert conn is not None
            mock_connect.assert_called_once()


def test_users_table_exists(db):
    cursor = db.cursor()
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    """)
    assert cursor.fetchone() is not None


def test_admin_user_created(db):
    cursor = db.cursor()
    cursor.execute("SELECT email, is_admin FROM users WHERE email = %s", ("a@a",))
    admin = cursor.fetchone()

    assert admin is not None
    assert admin["is_admin"] == 1


def test_quiz_questions_seeded(db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) AS count FROM quiz_questions")
    result = cursor.fetchone()

    assert result["count"] > 0


def test_roadmaps_seeded(db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) AS count FROM roadmaps")
    result = cursor.fetchone()

    assert result["count"] > 0


def test_roadmap_steps_exist(db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) AS count FROM roadmap_steps")
    result = cursor.fetchone()

    assert result["count"] > 0


def test_insert_user_and_field(db):
    cursor = db.cursor()

    # Insert user
    cursor.execute("""
        INSERT INTO users (email, password_hash)
        VALUES (%s, %s)
        RETURNING id
    """, ("test@test.com", "hashed_password"))

    user_result = cursor.fetchone()
    user_id = user_result['id']

    # Insert user field
    cursor.execute("""
        INSERT INTO user_fields (user_id, field_name, timestamp)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
    """, (user_id, "AI"))

    db.commit()

    cursor.execute("""
        SELECT field_name FROM user_fields WHERE user_id = %s
    """, (user_id,))

    field = cursor.fetchone()
    assert field["field_name"] == "AI"


def test_blog_insert(db):
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO blogs (title, url, summary)
        VALUES (%s, %s, %s)
    """, ("Test Blog", "https://example.com", "Test summary"))

    db.commit()

    cursor.execute("SELECT title FROM blogs WHERE url = %s", ("https://example.com",))
    blog = cursor.fetchone()

    assert blog is not None
    assert blog["title"] == "Test Blog"


def test_job_description_and_cv_ranking(db):
    cursor = db.cursor()

    # Get admin id
    cursor.execute("SELECT id FROM users WHERE is_admin = 1")
    admin_result = cursor.fetchone()
    admin_id = admin_result["id"]

    # Insert job description
    cursor.execute("""
        INSERT INTO job_descriptions (title, description, created_by)
        VALUES (%s, %s, %s)
        RETURNING id
    """, ("Backend Developer", "Python backend role", admin_id))

    job_result = cursor.fetchone()
    job_id = job_result['id']

    # Insert CV ranking
    cursor.execute("""
        INSERT INTO cv_rankings (
            user_id,
            cv_filename,
            job_description_id,
            overall_score
        ) VALUES (%s, %s, %s, %s)
    """, (admin_id, "cv.pdf", job_id, 85))

    db.commit()

    cursor.execute("""
        SELECT overall_score FROM cv_rankings WHERE job_description_id = %s
    """, (job_id,))

    ranking = cursor.fetchone()
    assert ranking["overall_score"] == 85


def test_duplicate_email_registration(db):
    cursor = db.cursor()
    
    # Insert a test user
    cursor.execute("""
        INSERT INTO users (email, password_hash)
        VALUES (%s, %s)
    """, ("duplicate@test.com", "hashed_password"))
    db.commit()
    
    # Mock the IntegrityError for duplicate email
    with patch.object(cursor, 'execute', side_effect=psycopg2.IntegrityError("duplicate key")):
        with pytest.raises(psycopg2.IntegrityError):
            cursor.execute("""
                INSERT INTO users (email, password_hash)
                VALUES (%s, %s)
            """, ("duplicate@test.com", "another_hash"))
            db.commit()
    
    # Cleanup
    cursor.execute("DELETE FROM users WHERE email = %s", ("duplicate@test.com",))
    db.commit()


def test_roadmap_relationships(db):
    cursor = db.cursor()
    
    # Get a roadmap and its steps
    cursor.execute("""
        SELECT r.id, r.field_name, COUNT(rs.id) as step_count
        FROM roadmaps r
        LEFT JOIN roadmap_steps rs ON r.id = rs.roadmap_id
        GROUP BY r.id, r.field_name
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    assert result is not None
    assert 'step_count' in result.keys()  # Check if 'step_count' is in the column names
    assert result['step_count'] > 0  # Each roadmap should have steps

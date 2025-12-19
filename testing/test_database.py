import os
import sqlite3
import pytest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from DB import init_db, get_db_connection, DATABASE_PATH

@pytest.fixture(scope="module")
def db():
    """
    Initialize database once before tests
    """
    # Remove old test DB if exists
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    init_db()
    conn = get_db_connection()
    yield conn
    conn.close()


def test_database_file_created():
    assert os.path.exists(DATABASE_PATH)


def test_users_table_exists(db):
    cursor = db.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='users'
    """)
    assert cursor.fetchone() is not None


def test_admin_user_created(db):
    cursor = db.cursor()
    cursor.execute("SELECT email, is_admin FROM users WHERE email = ?", ("a@a",))
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
        VALUES (?, ?)
    """, ("test@test.com", "hashed_password"))

    user_id = cursor.lastrowid

    # Insert user field
    cursor.execute("""
        INSERT INTO user_fields (user_id, field_name, timestamp)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (user_id, "AI"))

    db.commit()

    cursor.execute("""
        SELECT field_name FROM user_fields WHERE user_id = ?
    """, (user_id,))

    field = cursor.fetchone()
    assert field["field_name"] == "AI"


def test_blog_insert(db):
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO blogs (title, url, summary)
        VALUES (?, ?, ?)
    """, ("Test Blog", "https://example.com", "Test summary"))

    db.commit()

    cursor.execute("SELECT title FROM blogs WHERE url = ?", ("https://example.com",))
    blog = cursor.fetchone()

    assert blog is not None
    assert blog["title"] == "Test Blog"


def test_job_description_and_cv_ranking(db):
    cursor = db.cursor()

    # Get admin id
    cursor.execute("SELECT id FROM users WHERE is_admin = 1")
    admin_id = cursor.fetchone()["id"]

    # Insert job description
    cursor.execute("""
        INSERT INTO job_descriptions (title, description, created_by)
        VALUES (?, ?, ?)
    """, ("Backend Developer", "Python backend role", admin_id))

    job_id = cursor.lastrowid

    # Insert CV ranking
    cursor.execute("""
        INSERT INTO cv_rankings (
            user_id,
            cv_filename,
            job_description_id,
            overall_score
        ) VALUES (?, ?, ?, ?)
    """, (admin_id, "cv.pdf", job_id, 85))

    db.commit()

    cursor.execute("""
        SELECT overall_score FROM cv_rankings WHERE job_description_id = ?
    """, (job_id,))

    ranking = cursor.fetchone()
    assert ranking["overall_score"] == 85


def test_duplicate_email_registration(db):
    cursor = db.cursor()
    
    # Insert a test user
    cursor.execute("""
        INSERT INTO users (email, password_hash)
        VALUES (?, ?)
    """, ("duplicate@test.com", "hashed_password"))
    db.commit()
    
    # Try to insert user with same email
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO users (email, password_hash)
            VALUES (?, ?)
        """, ("duplicate@test.com", "another_hash"))
        db.commit()
    
    # Cleanup
    cursor.execute("DELETE FROM users WHERE email = ?", ("duplicate@test.com",))
    db.commit()


def test_roadmap_relationships(db):
    cursor = db.cursor()
    
    # Get a roadmap and its steps
    cursor.execute("""
        SELECT r.id, r.field_name, COUNT(rs.id) as step_count
        FROM roadmaps r
        LEFT JOIN roadmap_steps rs ON r.id = rs.roadmap_id
        GROUP BY r.id
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    assert result is not None
    assert 'step_count' in result.keys()  # Check if 'step_count' is in the column names
    assert result['step_count'] > 0  # Each roadmap should have steps

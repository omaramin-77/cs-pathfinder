# db_check.py
import sys
from DB import init_db, get_db_connection

def main():
    # Initialize DB (creates instance/database.db, tables, and seeds questions)
    init_db()

    conn = get_db_connection()
    cur = conn.cursor()

    required_tables = ["users", "quiz_questions", "user_fields", "roadmap_progress"]

    # Check that all required tables exist
    for table in required_tables:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        if not cur.fetchone():
            print(f" Missing table: {table}")
            conn.close()
            sys.exit(1)

    # Check that quiz questions are seeded
    cur.execute("SELECT COUNT(*) FROM quiz_questions")
    count = cur.fetchone()[0]
    if count < 20:
        print(f" Expected at least 20 quiz questions, found {count}")
        conn.close()
        sys.exit(1)

    conn.close()
    print(" Database schema and seed look correct.")

if __name__ == "__main__":
    main()
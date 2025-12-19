"""Simple database smoke test.

This script verifies that `database.init_db()` and `database.get_db_connection()`
work as expected. It uses a temporary database file `instance/test_database.db`
so it doesn't interfere with the main application database.

Run:
    python test_database.py
"""

import os
import sqlite3
import traceback

import database


TEST_DB_PATH = os.path.join('instance', 'test_database.db')


def run_smoke_tests():
    # Use a separate test database by overriding the module-level constant
    database.DATABASE_PATH = TEST_DB_PATH

    # Ensure clean start
    remove_test_db()

    try:
        print('Initializing test database...')
        database.init_db()

        conn = database.get_db_connection()
        cur = conn.cursor()

        # 1) Ensure quiz_questions table has rows (init_db inserts sample questions)
        cur.execute('SELECT COUNT(*) as cnt FROM quiz_questions')
        cnt = cur.fetchone()['cnt']
        print('quiz_questions count =', cnt)
        assert cnt > 0, 'quiz_questions table should contain sample rows'

        # 2) Insert a test user and read it back
        test_email = 'test_db_user@example.com'
        test_hash = 'fake-hash'
        cur.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (test_email, test_hash))
        conn.commit()

        cur.execute('SELECT * FROM users WHERE email = ?', (test_email,))
        user = cur.fetchone()
        print('Inserted user:', dict(user))
        assert user is not None and user['email'] == test_email

        # 3) Insert a user_fields row and read it back
        cur.execute('INSERT INTO user_fields (user_id, field_name, timestamp) VALUES (?, ?, ?)',
                    (user['id'], 'Test Field', 'now'))
        conn.commit()

        cur.execute('SELECT * FROM user_fields WHERE user_id = ?', (user['id'],))
        uf = cur.fetchone()
        print('Inserted user_fields:', dict(uf))
        assert uf is not None and uf['field_name'] == 'Test Field'

        print('\nDatabase smoke tests passed successfully.')

    except Exception:
        print('\nDatabase smoke tests failed:')
        traceback.print_exc()
        raise

    finally:
        try:
            conn.close()
        except Exception:
            pass
        # Cleanup test DB file
        remove_test_db()


def remove_test_db():
    try:
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
    except Exception:
        pass
    
if __name__ == '__main__':
    run_smoke_tests()

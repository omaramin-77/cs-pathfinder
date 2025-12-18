# Database setup and initialization
import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE_PATH = 'instance/database.db'

def get_db_connection():
    """Create and return a database connection"""
    # Ensure instance folder exists
    os.makedirs('instance', exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initialize database with tables and sample data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Create quiz_questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL
        )
    ''')
    
    # Create user_fields table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create roadmap_progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmap_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            step_number INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create blogs table (include fields for full scraped content)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            summary TEXT,
            full_text TEXT,
            author TEXT,
            thumbnail TEXT,
            published_date TEXT,
            scraped_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            image_url TEXT
        )
    ''')

    # Add missing columns if needed
    cursor.execute("PRAGMA table_info(blogs)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    for col_name, col_def in [('full_text', 'TEXT'), ('author', 'TEXT'), ('thumbnail', 'TEXT'), 
                               ('scraped_at', 'TEXT'), ('image_url', 'TEXT')]:
        if col_name not in existing_cols:
            try:
                cursor.execute(f'ALTER TABLE blogs ADD COLUMN {col_name} {col_def}')
            except Exception:
                pass
    
    # Create roadmaps table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create roadmap_steps table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmap_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roadmap_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            step_text TEXT NOT NULL,
            description TEXT NOT NULL,
            course_url TEXT NOT NULL,
            FOREIGN KEY (roadmap_id) REFERENCES roadmaps (id),
            UNIQUE(roadmap_id, step_number)
        )
    ''')
    
    # Create job_descriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Create cv_rankings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cv_rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            cv_filename TEXT NOT NULL,
            job_description_id INTEGER,
            custom_job_description TEXT,
            overall_score INTEGER,
            matching_analysis TEXT,
            description TEXT,
            recommendation TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (job_description_id) REFERENCES job_descriptions (id)
        )
    ''')
    
    # Check if questions already exist
    cursor.execute('SELECT COUNT(*) as count FROM quiz_questions')
    existing = cursor.fetchone()
    
    if existing[0] == 0:
        # Import and insert quiz questions from data file
        from data.questions_data import QUESTIONS
        
        print("❓ Seeding quiz questions...")
        cursor.executemany('''
            INSERT INTO quiz_questions (question_text, option_a, option_b, option_c, option_d)
            VALUES (?, ?, ?, ?, ?)
        ''', QUESTIONS)
        print(f"✅ Seeded {len(QUESTIONS)} quiz questions")
    
    # Check if admin user exists, create default admin if not
    cursor.execute('SELECT id FROM users WHERE email = ?', ('a@a',))
    admin_user = cursor.fetchone()
    
    if not admin_user:
        # Create default admin user
        admin_password_hash = generate_password_hash('123456')
        cursor.execute('''
            INSERT INTO users (email, password_hash, is_admin)
            VALUES (?, ?, ?)
        ''', ('a@a', admin_password_hash, 1))
        admin_id = cursor.lastrowid
        print("✅ Default admin user created: a@a / 123456")
    else:
        admin_id = admin_user['id']
    
    # Check if roadmaps already exist
    cursor.execute('SELECT COUNT(*) as count FROM roadmaps')
    roadmap_count = cursor.fetchone()
    
    if roadmap_count[0] == 0:
        # Import and seed roadmaps from data file
        from data.roadmaps_data import ROADMAPS
        
        print("📚 Seeding roadmaps from data/roadmaps_data.py...")
        for field_name, steps in ROADMAPS.items():
            cursor.execute('INSERT INTO roadmaps (field_name) VALUES (?)', (field_name,))
            roadmap_id = cursor.lastrowid
            
            for step_number, step_data in enumerate(steps, 1):
                cursor.execute('''
                    INSERT INTO roadmap_steps (roadmap_id, step_number, step_text, description, course_url)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    roadmap_id,
                    step_number,
                    step_data['text'],
                    step_data['description'],
                    step_data['course']
                ))
        print(f"✅ Seeded {len(ROADMAPS)} roadmaps")
    
    # Check if job descriptions already exist
    cursor.execute('SELECT COUNT(*) as count FROM job_descriptions')
    job_desc_count = cursor.fetchone()
    
    if job_desc_count[0] == 0:
        # Import and seed job descriptions from data file
        from data.job_descriptions_data import JOB_DESCRIPTIONS
        
        print("💼 Seeding job descriptions...")
        for job in JOB_DESCRIPTIONS:
            cursor.execute('''
                INSERT INTO job_descriptions (title, description, created_by)
                VALUES (?, ?, ?)
            ''', (job['title'], job['description'], admin_id))
        print(f"✅ Seeded {len(JOB_DESCRIPTIONS)} job descriptions")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__ == '__main__':
    init_db()

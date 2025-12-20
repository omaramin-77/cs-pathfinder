# Database setup and initialization for PostgreSQL
import psycopg2
import psycopg2.extras
import os
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load .env file (local development only)
load_dotenv()

def should_run_db_init():
    """
    Controls whether database initialization should run.
    Intended to be enabled ONCE in production.
    """
    return os.getenv("RUN_DB_INIT") == "1"


def get_db_connection():
    """Create and return a PostgreSQL database connection"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    return psycopg2.connect(
        database_url,
        cursor_factory=psycopg2.extras.RealDictCursor,
        sslmode="require"
    )


def init_db():
    """Initialize database with tables and sample data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        ''')
        
        # Create quiz_questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                field_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create roadmap_progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roadmap_progress (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                field_name TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create blogs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blogs (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                summary TEXT,
                full_text TEXT,
                author TEXT,
                thumbnail TEXT,
                published_date TEXT,
                scraped_at TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_url TEXT
            )
        ''')
        
        # Create roadmaps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roadmaps (
                id SERIAL PRIMARY KEY,
                field_name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create roadmap_steps table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roadmap_steps (
                id SERIAL PRIMARY KEY,
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
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Create cv_rankings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cv_rankings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                cv_filename TEXT NOT NULL,
                job_description_id INTEGER,
                custom_job_description TEXT,
                overall_score INTEGER,
                matching_analysis TEXT,
                description TEXT,
                recommendation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (job_description_id) REFERENCES job_descriptions (id)
            )
        ''')
        
        # Commit table creation
        conn.commit()
        
        # Check if questions already exist
        cursor.execute('SELECT COUNT(*) as count FROM quiz_questions')
        existing = cursor.fetchone()
        
        if existing['count'] == 0:
            # Import and insert quiz questions from data file
            try:
                from data.questions_data import QUESTIONS
                
                print("❓ Seeding quiz questions...")
                cursor.executemany('''
                    INSERT INTO quiz_questions (question_text, option_a, option_b, option_c, option_d)
                    VALUES (%s, %s, %s, %s, %s)
                ''', QUESTIONS)
                conn.commit()
                print(f"✅ Seeded {len(QUESTIONS)} quiz questions")
            except ImportError:
                print("⚠️ questions_data.py not found, skipping quiz questions seeding")
        
        # Check if admin user exists, create default admin if not
        cursor.execute('SELECT id FROM users WHERE email = %s', ('a@a',))
        admin_user = cursor.fetchone()
        
        if not admin_user:
            # Create default admin user
            admin_password_hash = generate_password_hash('123456')
            cursor.execute('''
                INSERT INTO users (email, password_hash, is_admin)
                VALUES (%s, %s, %s)
                RETURNING id
            ''', ('a@a', admin_password_hash, 1))
            admin_result = cursor.fetchone()
            admin_id = admin_result['id']
            conn.commit()
            print("✅ Default admin user created: a@a / 123456")
        else:
            admin_id = admin_user['id']
        
        # Check if roadmaps already exist
        cursor.execute('SELECT COUNT(*) as count FROM roadmaps')
        roadmap_count = cursor.fetchone()
        
        if roadmap_count['count'] == 0:
            # Import and seed roadmaps from data file
            try:
                from data.roadmaps_data import ROADMAPS
                
                print("📚 Seeding roadmaps from data/roadmaps_data.py...")
                for field_name, steps in ROADMAPS.items():
                    cursor.execute('INSERT INTO roadmaps (field_name) VALUES (%s) RETURNING id', (field_name,))
                    roadmap_result = cursor.fetchone()
                    roadmap_id = roadmap_result['id']
                    
                    for step_number, step_data in enumerate(steps, 1):
                        cursor.execute('''
                            INSERT INTO roadmap_steps (roadmap_id, step_number, step_text, description, course_url)
                            VALUES (%s, %s, %s, %s, %s)
                        ''', (
                            roadmap_id,
                            step_number,
                            step_data['text'],
                            step_data['description'],
                            step_data['course']
                        ))
                conn.commit()
                print(f"✅ Seeded {len(ROADMAPS)} roadmaps")
            except ImportError:
                print("⚠️ roadmaps_data.py not found, skipping roadmaps seeding")
        
        # Check if job descriptions already exist
        cursor.execute('SELECT COUNT(*) as count FROM job_descriptions')
        job_desc_count = cursor.fetchone()
        
        if job_desc_count['count'] == 0:
            # Import and seed job descriptions from data file
            try:
                from data.job_descriptions_data import JOB_DESCRIPTIONS
                
                print("💼 Seeding job descriptions...")
                for job in JOB_DESCRIPTIONS:
                    cursor.execute('''
                        INSERT INTO job_descriptions (title, description, created_by)
                        VALUES (%s, %s, %s)
                    ''', (job['title'], job['description'], admin_id))
                conn.commit()
                print(f"✅ Seeded {len(JOB_DESCRIPTIONS)} job descriptions")
            except ImportError:
                print("⚠️ job_descriptions_data.py not found, skipping job descriptions seeding")
        
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Database initialization error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    if should_run_db_init():
        print("🚀 RUN_DB_INIT=1 detected — initializing database...")
        init_db()
        print("✅ Database initialization completed.")
    else:
        print("ℹ️ RUN_DB_INIT not set — skipping database initialization.")

# Database setup and initialization
import sqlite3
import os

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
            password_hash TEXT NOT NULL
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
    
    # Check if questions already exist
    existing = cursor.execute('SELECT COUNT(*) as count FROM quiz_questions').fetchone()
    
    if existing[0] == 0:
        # Insert 20 sample quiz questions
        questions = [
            ("What interests you most?", "Building AI models", "Creating websites", "Protecting systems", "Analyzing data"),
            ("Which activity sounds most appealing?", "Training neural networks", "Designing user interfaces", "Finding vulnerabilities", "Creating visualizations"),
            ("What's your preferred work style?", "Research and experimentation", "Creative design", "Problem solving", "Data exploration"),
            ("Which technology excites you?", "Machine Learning", "React/Vue", "Encryption", "Big Data"),
            ("What's your math comfort level?", "Love advanced math", "Basic math is fine", "Moderate math", "Statistics focused"),
            ("Preferred programming focus?", "Python/TensorFlow", "JavaScript/HTML/CSS", "C/Assembly", "Python/R"),
            ("What motivates you?", "Innovation", "User experience", "Security", "Insights"),
            ("Which project sounds fun?", "Chatbot", "E-commerce site", "Penetration testing", "Sales dashboard"),
            ("Your ideal work environment?", "Research lab", "Startup", "Security firm", "Analytics team"),
            ("What do you want to learn?", "Deep learning", "Frontend frameworks", "Network security", "SQL and databases"),
            ("Which skill do you have?", "Math and statistics", "Design sense", "Logical thinking", "Analytical mindset"),
            ("Preferred industry?", "AI/Robotics", "Tech/Media", "Finance/Government", "Business/Consulting"),
            ("What's your goal?", "Build intelligent systems", "Create beautiful apps", "Prevent cyber attacks", "Drive decisions with data"),
            ("Which tool interests you?", "PyTorch", "Figma", "Wireshark", "Tableau"),
            ("How do you solve problems?", "Experiment with models", "Iterate on design", "Think like an attacker", "Analyze patterns"),
            ("What's your learning style?", "Research papers", "Tutorials and videos", "Hands-on labs", "Case studies"),
            ("Which career path appeals to you?", "AI Researcher", "Full-stack Developer", "Security Analyst", "Data Analyst"),
            ("What's your favorite subject?", "Artificial Intelligence", "Web Development", "Cryptography", "Statistics"),
            ("Which outcome excites you?", "Model accuracy improvement", "Smooth user experience", "Zero vulnerabilities", "Actionable insights"),
            ("What's your dream project?", "Self-driving car AI", "Social media platform", "Security audit tool", "Predictive analytics system")
        ]
        
        cursor.executemany('''
            INSERT INTO quiz_questions (question_text, option_a, option_b, option_c, option_d)
            VALUES (?, ?, ?, ?, ?)
        ''', questions)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()

# cs-pathfinder
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
    

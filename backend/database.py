import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

def init_db(db_path=DB_PATH):
    """Initialize the database with necessary tables."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Articles table
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  url TEXT UNIQUE NOT NULL,
                  title TEXT NOT NULL,
                  content TEXT,
                  published_at TIMESTAMP NOT NULL,
                  source_type TEXT,
                  source_name TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Summaries table
    c.execute('''CREATE TABLE IF NOT EXISTS summaries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timeframe TEXT NOT NULL,
                  summary_text TEXT NOT NULL,
                  article_count INTEGER,
                  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Indexes for performance
    c.execute('CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_summaries_timeframe ON summaries(timeframe, generated_at)')
    
    conn.commit()
    conn.close()

def get_db_connection(db_path=DB_PATH):
    """Get a connection to the database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

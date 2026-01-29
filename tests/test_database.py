import os
import sqlite3
import pytest
from backend.database import init_db, get_db_connection

# Use a temporary file for testing
TEST_DB = 'test_data.db'

@pytest.fixture
def db_path():
    yield TEST_DB
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_init_db(db_path):
    init_db(db_path)
    assert os.path.exists(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    assert 'articles' in tables
    assert 'summaries' in tables
    
    conn.close()

def test_insert_article(db_path):
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO articles (url, title, content, published_at, source_type, source_name)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   ('http://example.com', 'Test Title', 'Content', '2023-01-01 12:00:00', 'blog', 'Test Source'))
    conn.commit()
    
    cursor.execute('SELECT * FROM articles WHERE url = ?', ('http://example.com',))
    article = cursor.fetchone()
    assert article['title'] == 'Test Title'
    
    conn.close()

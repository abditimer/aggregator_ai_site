from fastapi.testclient import TestClient
from backend.api import app, DB_PATH
import sqlite3
import os
import pytest

client = TestClient(app)
TEST_DB = 'test_api.db'

# Override DB path for testing (Mocking DB connection in api.py is harder without dependency injection, 
# so we might need to patch sqlite3.connect or modify api.py to accept db_path)
# For simplicity, we'll patch backend.api.DB_PATH or patch sqlite3.connect.

@pytest.fixture
def mock_db():
    # Setup test DB
    conn = sqlite3.connect(TEST_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  url TEXT, title TEXT, content TEXT, published_at TIMESTAMP, source_type TEXT, source_name TEXT, created_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS summaries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timeframe TEXT, summary_text TEXT, article_count INTEGER, generated_at TIMESTAMP)''')
    
    # Insert Data
    c.execute("INSERT INTO articles (url, title, published_at, source_name) VALUES (?, ?, datetime('now'), ?)",
              ('http://test.com', 'Test API Article', 'API Source'))
    c.execute("INSERT INTO summaries (timeframe, summary_text, article_count) VALUES (?, ?, ?)",
              ('7d', 'Test API Summary', 1))
    conn.commit()
    conn.close()
    
    yield TEST_DB
    
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

# We need to patch DB_PATH in api.py
from unittest.mock import patch

def test_read_summary(mock_db):
    with patch('backend.api.DB_PATH', TEST_DB):
        response = client.get("/summaries/7d")
        assert response.status_code == 200
        assert response.json()['summary'] == 'Test API Summary'

def test_read_articles(mock_db):
    with patch('backend.api.DB_PATH', TEST_DB):
        response = client.get("/articles/7d")
        assert response.status_code == 200
        assert len(response.json()) >= 1
        assert response.json()[0]['title'] == 'Test API Article'

def test_invalid_timeframe(mock_db):
    with patch('backend.api.DB_PATH', TEST_DB):
        response = client.get("/articles/invalid")
        assert response.status_code == 400

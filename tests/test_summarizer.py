import unittest
from unittest.mock import patch, MagicMock
from backend.summarizer import generate_summary
import sqlite3
import os

TEST_DB = 'test_summarizer.db'

class TestSummarizer(unittest.TestCase):
    
    def setUp(self):
        self.conn = sqlite3.connect(TEST_DB)
        c = self.conn.cursor()
        c.execute('''CREATE TABLE articles
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      url TEXT UNIQUE NOT NULL,
                      title TEXT NOT NULL,
                      content TEXT,
                      published_at TIMESTAMP NOT NULL,
                      source_type TEXT,
                      source_name TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE summaries
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timeframe TEXT NOT NULL,
                      summary_text TEXT NOT NULL,
                      article_count INTEGER,
                      generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Insert test data
        c.execute("INSERT INTO articles (url, title, content, published_at, source_name) VALUES (?, ?, ?, datetime('now'), ?)",
                  ('http://test1.com', 'Article 1', 'Content 1', 'Source A'))
        conn = self.conn.commit()

    def tearDown(self):
        self.conn.close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    @patch('backend.summarizer.ollama.chat')
    def test_generate_summary(self, mock_chat):
        # Mock LLM Response
        mock_response = {'message': {'content': 'This is a test summary.'}}
        mock_chat.return_value = mock_response
        
        summary = generate_summary(1, db_path=TEST_DB)
        
        self.assertEqual(summary, 'This is a test summary.')
        
        # Check DB
        c = self.conn.cursor()
        c.execute("SELECT * FROM summaries")
        row = c.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[2], 'This is a test summary.') # summary_text is 3rd column (0-indexed 2? id, timeframe, summary_text)
        # Schema: id, timeframe, summary_text, article_count, ...
        # id=1, timeframe='1d', summary_text='...', count=1

if __name__ == '__main__':
    unittest.main()

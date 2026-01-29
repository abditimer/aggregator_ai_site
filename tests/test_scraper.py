import unittest
from unittest.mock import patch, MagicMock
from backend.scraper import scrape_blogs
import sqlite3
import os

TEST_DB = 'test_scraper.db'

class TestScraper(unittest.TestCase):
    
    def setUp(self):
        # Create a fresh temp database
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
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    @patch('backend.scraper.feedparser.parse')
    def test_scrape_blogs(self, mock_parse):
        # Create different feeds for each call
        def create_mock_feed(url):
            mock_feed = MagicMock()
            mock_feed.bozo = 0
            mock_entry = MagicMock()
            mock_entry.title = f"Test Article from {url}"
            mock_entry.link = f"{url}/article"
            mock_entry.summary = "Test Summary"
            # Ensure content attribute doesn't exist so it uses summary
            del mock_entry.content
            mock_entry.published_parsed = (2023, 1, 1, 12, 0, 0, 0, 0, 0)
            mock_feed.entries = [mock_entry]
            return mock_feed

        mock_parse.side_effect = create_mock_feed
        
        # Run scraper with test db
        count = scrape_blogs(db_path=TEST_DB)
        
        self.assertEqual(count, 4) # Should be 4 now that URLs are unique
        
        c = self.conn.cursor()
        c.execute("SELECT * FROM articles")
        rows = c.fetchall()
        # Should have 4 rows
        self.assertEqual(len(rows), 4)

if __name__ == '__main__':
    unittest.main()

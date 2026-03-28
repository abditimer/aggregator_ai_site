"""Tests that verify article URLs are valid and trend summaries don't contain hallucinated article IDs."""
import json
import os
import re
import sqlite3
import unittest
from unittest.mock import patch, MagicMock

from backend.scraper import is_valid_url, scrape_blogs

VALID_URL_RE = re.compile(r'^https?://\S+')

DATA_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'frontend', 'public', 'data.json',
)

TEST_DB = 'test_links.db'


class TestUrlValidationHelper(unittest.TestCase):
    """Unit tests for the is_valid_url helper in scraper.py."""

    def test_accepts_http_url(self):
        self.assertTrue(is_valid_url('http://example.com/article'))

    def test_accepts_https_url(self):
        self.assertTrue(is_valid_url('https://openai.com/blog/post'))

    def test_rejects_empty_string(self):
        self.assertFalse(is_valid_url(''))

    def test_rejects_none_equivalent(self):
        self.assertFalse(is_valid_url(None))

    def test_rejects_relative_url(self):
        self.assertFalse(is_valid_url('/news/some-article'))

    def test_rejects_protocol_relative(self):
        self.assertFalse(is_valid_url('//example.com/article'))


class TestScraperRejectsInvalidUrls(unittest.TestCase):
    """Verify the scraper does not persist articles with invalid URLs."""

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
                      summary TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    @patch('backend.scraper.feedparser.parse')
    def test_invalid_url_entry_not_stored(self, mock_parse):
        """Entries without a valid URL must be skipped by the RSS scraper."""

        def make_feed(url):
            feed = MagicMock()
            feed.bozo = 0
            good_entry = MagicMock()
            good_entry.title = 'Good Article'
            good_entry.link = f'{url}/good-article'
            good_entry.summary = 'summary'
            del good_entry.content
            good_entry.published_parsed = (2024, 1, 1, 0, 0, 0, 0, 0, 0)

            bad_entry = MagicMock()
            bad_entry.title = 'Bad Article'
            bad_entry.link = '/relative/path'        # relative — should be rejected
            bad_entry.summary = 'summary'
            del bad_entry.content
            bad_entry.published_parsed = (2024, 1, 1, 0, 0, 0, 0, 0, 0)

            feed.entries = [good_entry, bad_entry]
            return feed

        mock_parse.side_effect = make_feed
        scrape_blogs(db_path=TEST_DB)

        c = self.conn.cursor()
        c.execute("SELECT url FROM articles")
        stored_urls = [row[0] for row in c.fetchall()]

        for url in stored_urls:
            self.assertTrue(
                VALID_URL_RE.match(url),
                f"Stored URL is not a valid absolute URL: {url!r}",
            )

    @patch('backend.scraper.feedparser.parse')
    def test_empty_url_entry_not_stored(self, mock_parse):
        """Entries with an empty/None URL must be skipped."""

        def make_feed(url):
            feed = MagicMock()
            feed.bozo = 0
            entry = MagicMock()
            entry.title = 'No URL Article'
            entry.link = ''
            entry.summary = 'summary'
            del entry.content
            entry.published_parsed = (2024, 1, 1, 0, 0, 0, 0, 0, 0)
            feed.entries = [entry]
            return feed

        mock_parse.side_effect = make_feed
        scrape_blogs(db_path=TEST_DB)

        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM articles")
        count = c.fetchone()[0]
        self.assertEqual(count, 0, "Articles with empty URLs should not be stored")


class TestDataJsonLinks(unittest.TestCase):
    """Integration-style tests against the committed frontend/public/data.json snapshot."""

    @classmethod
    def setUpClass(cls):
        if os.path.exists(DATA_JSON_PATH):
            with open(DATA_JSON_PATH) as f:
                cls.data = json.load(f)
        else:
            cls.data = None

    def _skip_if_no_data(self):
        if self.data is None:
            self.skipTest('frontend/public/data.json not found')

    def test_all_articles_have_valid_urls(self):
        """Every article in data.json must have a non-empty absolute URL."""
        self._skip_if_no_data()
        for article in self.data['articles']:
            url = article.get('url', '')
            self.assertTrue(url, f"Article '{article.get('title')}' has empty URL")
            self.assertRegex(
                url, VALID_URL_RE,
                f"Article '{article.get('title')}' has invalid URL: {url!r}",
            )

    def test_no_duplicate_article_urls(self):
        """No two articles in data.json may share the same URL."""
        self._skip_if_no_data()
        urls = [a['url'] for a in self.data['articles']]
        duplicates = len(urls) - len(set(urls))
        self.assertEqual(duplicates, 0, f"Found {duplicates} duplicate article URLs")

    def test_trend_article_ids_reference_real_articles(self):
        """article_ids in every trend summary must correspond to real article IDs."""
        self._skip_if_no_data()
        real_ids = {a['id'] for a in self.data['articles']}
        for timeframe, summary in self.data.get('summaries', {}).items():
            if not summary or not summary.get('summary'):
                continue
            try:
                parsed = json.loads(summary['summary'])
            except (json.JSONDecodeError, TypeError):
                continue  # Non-JSON summaries (1d/7d text) are fine
            for trend in parsed.get('trends', []):
                for aid in trend.get('article_ids', []):
                    self.assertIn(
                        aid, real_ids,
                        f"Trend '{trend.get('name')}' in timeframe '{timeframe}' "
                        f"references non-existent article ID {aid}",
                    )

    def test_articles_list_is_non_empty(self):
        """data.json must contain at least one article."""
        self._skip_if_no_data()
        self.assertGreater(len(self.data['articles']), 0, "data.json articles list is empty")


if __name__ == '__main__':
    unittest.main()

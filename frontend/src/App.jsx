import { useState, useEffect } from 'react';
import TimeframeSelector from './components/TimeframeSelector';
import SummaryCard from './components/SummaryCard';
import ArticleStream from './components/ArticleStream';
import ReactMarkdown from 'react-markdown';

const API_Base = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('7d');
  const [articles, setArticles] = useState([]);
  const [trendSummary, setTrendSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedTrend, setSelectedTrend] = useState(null);

  // Pagination State
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isFetchingMore, setIsFetchingMore] = useState(false);

  useEffect(() => {
    // Reset on tab change
    setArticles([]);
    setPage(1);
    setHasMore(true);
    setTrendSummary(null);
    setSelectedTrend(null);
  }, [activeTab]);

  useEffect(() => {
    async function fetchData() {
      if (!hasMore && page > 1) return;

      setLoading(page === 1);
      setIsFetchingMore(page > 1);

      try {
        const requests = [fetch(`${API_Base}/articles/${activeTab}?page=${page}&limit=20`)];

        // Fetch Trend Summary only for long timeframes AND only first page
        if ((activeTab === '30d' || activeTab === '1y') && page === 1) {
          requests.push(fetch(`${API_Base}/summaries/${activeTab}`));
        }

        const responses = await Promise.all(requests);
        const articlesRes = responses[0];

        if (articlesRes.ok) {
          const newArticles = await articlesRes.json();

          if (newArticles.length < 20) {
            setHasMore(false);
          }

          setArticles(prev => {
            if (page === 1) return newArticles;
            // Check for dups based on ID
            const existingIds = new Set(prev.map(a => a.id));
            const uniqueNew = newArticles.filter(a => !existingIds.has(a.id));
            return [...prev, ...uniqueNew];
          });
        }

        // Handle summary (only if requested)
        if (responses.length > 1 && responses[1] && responses[1].ok) {
          const summaryRes = responses[1];
          const summaryData = await summaryRes.json();
          if (!summaryData.error && summaryData.summary) {
            try {
              const parsed = JSON.parse(summaryData.summary);
              setTrendSummary({ ...summaryData, parsed });
            } catch (e) {
              console.error("Failed to parse trend summary JSON", e);
            }
          }
        }

      } catch (error) {
        console.error("Failed to fetch data", error);
      } finally {
        setLoading(false);
        setIsFetchingMore(false);
      }
    }

    fetchData();
  }, [activeTab, page]);

  const loadMore = () => {
    if (!loading && !isFetchingMore && hasMore) {
      setPage(prev => prev + 1);
    }
  };

  return (
    <div className="min-h-screen bg-cream selection:bg-black selection:text-white">
      <div className="max-w-3xl mx-auto px-6 py-12 md:py-20">

        {/* Header */}
        <header className="mb-12">
          <h1 className="text-4xl md:text-5xl font-serif font-bold text-text-main mb-2 tracking-tight">
            AI News
          </h1>
          <h2 className="text-xl font-serif text-gray-600 italic mb-4">
            Summarised by Abdi Timer and his AI Team
          </h2>
          <p className="text-gray-400 font-sans text-sm uppercase tracking-widest">
            Curated updates from the frontier of intelligence.
          </p>
        </header>

        {/* Navigation */}
        <TimeframeSelector activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Content */}
        <main>
          {/* Trend Chips (Interactive) */}
          {trendSummary && trendSummary.parsed && (
            <div className="mb-12">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-xs font-bold text-openai uppercase tracking-widest">Trend Analysis</span>
                <span className="text-xs text-gray-400">Filter by major themes</span>
              </div>

              <div className="flex flex-wrap gap-4">
                <button
                  onClick={() => setSelectedTrend(null)}
                  className={`text-left p-4 rounded-lg border transition-all duration-200 flex-1 min-w-[200px] ${!selectedTrend
                    ? 'bg-black text-white border-black shadow-lg ring-1 ring-black'
                    : 'bg-white text-gray-500 border-gray-100 hover:border-gray-300'
                    }`}
                >
                  <h3 className="font-bold text-sm mb-1">All Trends</h3>
                  <p className="text-xs opacity-80">Show all {articles.length} articles</p>
                </button>

                {trendSummary.parsed.trends?.map((trend, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedTrend(trend)}
                    className={`text-left p-4 rounded-lg border transition-all duration-200 flex-1 min-w-[200px] ${selectedTrend === trend
                      ? 'bg-black text-white border-black shadow-lg ring-1 ring-black'
                      : 'bg-white text-gray-600 border-gray-100 hover:border-gray-300'
                      }`}
                  >
                    <h3 className="font-bold text-sm mb-1">{trend.name}</h3>
                    <p className="text-xs opacity-80 line-clamp-2">{trend.summary}</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="mb-8">
            <h2 className="text-sm font-sans font-bold text-gray-400 uppercase tracking-widest mb-6">
              Latest Articles
            </h2>
            <ArticleStream
              articles={articles}
              loading={loading}
              selectedTrend={selectedTrend}
              loadMore={loadMore}
              hasMore={hasMore}
            />
          </div>
        </main>

        <footer className="mt-20 pt-8 border-t border-gray-200 text-center text-gray-400 text-sm font-sans">
          <p>© {new Date().getFullYear()} AI News Summarised by Abdi Timer and his AI Team. All Rights Reserved.</p>
        </footer>

      </div>
    </div>
  );
}

export default App;

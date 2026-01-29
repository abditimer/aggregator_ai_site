#!/bin/bash

# exit on error
set -e

echo "🚀 Starting AI News Update Pipeline..."

# Ensure we are in the root directory
cd "$(dirname "$0")"

# 1. Scrape new articles
echo "--------------------------------"
echo "📡 Step 1/4: Scraping latest news..."
source backend/venv/bin/activate
python -m backend.scraper

# 2. Generate Summaries (requires Ollama running)
echo "--------------------------------"
echo "🧠 Step 2/4: Summarizing with Local LLM (Ollama)..."
# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Ollama is not running! Please start 'ollama serve' in another terminal."
    exit 1
fi
python -m backend.summarizer

# 3. Generate Static Data
echo "--------------------------------"
echo "💾 Step 3/4: Generating static snapshot..."
python scripts/generate_static_data.py

# 4. Build Frontend
echo "--------------------------------"
echo "🏗️  Step 4/4: Building static site..."
cd frontend
npm run build

echo "--------------------------------"
echo "✅ Update Complete!"
echo "To publish the changes to GitHub Pages, run:"
echo ""
echo "   git add ."
echo "   git commit -m \"Daily update: $(date +'%Y-%m-%d')\""
echo "   git push"
echo ""

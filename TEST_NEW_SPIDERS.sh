#!/bin/bash
# Test the 3 new spiders

cd /Users/macbookpro201916i964gb1tb/Downloads/YACHAQ-LEX_full/rag/ingest

echo "🕷️  Testing 3 NEW YACHAQ-LEX Spiders..."
echo "========================================="

echo ""
echo "1️⃣  Testing Presidencia Spider..."
scrapy crawl presidencia -o test_presidencia.jsonl -s CLOSESPIDER_PAGECOUNT=5

echo ""
echo "2️⃣  Testing Ministerio de Salud Spider..."
scrapy crawl ministerio_salud -o test_salud.jsonl -s CLOSESPIDER_PAGECOUNT=5

echo ""
echo "3️⃣  Testing Ministerio de Economía Spider..."
scrapy crawl ministerio_economia -o test_economia.jsonl -s CLOSESPIDER_PAGECOUNT=5

echo ""
echo "✅ Tests complete! Check output files:"
echo "   - test_presidencia.jsonl"
echo "   - test_salud.jsonl"
echo "   - test_economia.jsonl"
echo ""
echo "📊 Quick stats:"
wc -l test_*.jsonl

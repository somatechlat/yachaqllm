#!/bin/bash
# Start generating 1M questions with Groq API
# Run in background: nohup ./START_GENERATION.sh > generation.log 2>&1 &

if [ -z "${GROQ_API_KEY:-}" ]; then
	echo "GROQ_API_KEY is not set. Export it before running this script." >&2
	exit 1
fi

echo "Starting YACHAQ-LEX Q&A Generation"
echo "Target: 1,000,000 questions"
echo "Started: $(date)"
echo ""

python3 generate_hybrid.py

echo ""
echo "Complete: $(date)"

#!/bin/bash
set -e

# Simple script to run scrapers on existing AWS instance
# Usage: ./run_scrapers_aws.sh <instance-ip>

if [ -z "$1" ]; then
    echo "Usage: ./run_scrapers_aws.sh <instance-ip>"
    exit 1
fi

INSTANCE_IP=$1
KEY_FILE=~/.ssh/yachaq-scraper-key.pem

echo "Uploading scrapers to $INSTANCE_IP..."
scp -i $KEY_FILE -o StrictHostKeyChecking=no \
    rag/ingest/*.py ec2-user@${INSTANCE_IP}:~/yachaq-scraper/

echo "Starting scraping process..."
ssh -i $KEY_FILE -o StrictHostKeyChecking=no \
    ec2-user@${INSTANCE_IP} << 'ENDSSH'
cd ~/yachaq-scraper
nohup python3 scrape_all.py > scraper.log 2>&1 &
echo "Scraping started in background. Check scraper.log for progress."
ENDSSH

echo ""
echo "Scraping started on $INSTANCE_IP"
echo "To check progress:"
echo "  ssh -i $KEY_FILE ec2-user@${INSTANCE_IP} 'tail -f ~/yachaq-scraper/scraper.log'"
echo ""
echo "To download results:"
echo "  scp -i $KEY_FILE -r ec2-user@${INSTANCE_IP}:~/yachaq-scraper/downloads ."
echo "  scp -i $KEY_FILE ec2-user@${INSTANCE_IP}:~/yachaq-scraper/*.jsonl ."

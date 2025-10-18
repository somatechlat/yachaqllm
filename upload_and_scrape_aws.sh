#!/bin/bash
set -e

BUCKET="s3://yachaq-lex-raw-0017472631"
REGION="us-east-1"

echo "=== UPLOADING SCRAPERS TO AWS S3 ==="
aws s3 cp rag/ingest/ ${BUCKET}/scrapers/ --recursive --exclude "*" --include "*.py" --region ${REGION}

echo "=== UPLOADING EXISTING DATA ==="
aws s3 cp rag/ingest/ ${BUCKET}/data/ --recursive --exclude "*" --include "*.jsonl" --region ${REGION}
aws s3 cp rag/ingest/downloads/ ${BUCKET}/downloads/ --recursive --region ${REGION}

echo "=== CREATING EC2 SCRAPER INSTANCE ==="
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t3.xlarge \
    --key-name yachaq-key \
    --security-group-ids sg-default \
    --region ${REGION} \
    --user-data '#!/bin/bash
yum update -y
yum install -y python3 python3-pip
pip3 install requests beautifulsoup4 lxml boto3
mkdir -p /home/ec2-user/scrapers
aws s3 cp s3://yachaq-lex-raw-0017472631/scrapers/ /home/ec2-user/scrapers/ --recursive
cd /home/ec2-user/scrapers
nohup python3 scrape_all.py > scraper.log 2>&1 &
' \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=yachaq-scraper}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance launched: ${INSTANCE_ID}"
echo "Waiting for instance..."
aws ec2 wait instance-running --instance-ids ${INSTANCE_ID} --region ${REGION}

PUBLIC_IP=$(aws ec2 describe-instances --instance-ids ${INSTANCE_ID} --query 'Reservations[0].Instances[0].PublicIpAddress' --output text --region ${REGION})

echo ""
echo "=== SCRAPING STARTED ON AWS ==="
echo "Instance: ${INSTANCE_ID}"
echo "IP: ${PUBLIC_IP}"
echo "Scrapers running in background"
echo ""
echo "To check progress:"
echo "  aws s3 ls ${BUCKET}/downloads/"
echo ""
echo "To download results:"
echo "  aws s3 sync ${BUCKET}/downloads/ ./aws_downloads/"

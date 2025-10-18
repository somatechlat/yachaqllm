#!/bin/bash
set -e

# AWS Configuration
AWS_REGION="us-east-1"
EC2_KEY_NAME="yachaq-scraper-key"
INSTANCE_TYPE="t3.medium"
AMI_ID="ami-0c55b159cbfafe1f0"  # Amazon Linux 2023
SECURITY_GROUP="yachaq-scraper-sg"

echo "=========================================="
echo "YACHAQ-LEX AWS Deployment"
echo "=========================================="

# Create security group
echo "Creating security group..."
aws ec2 create-security-group \
    --group-name $SECURITY_GROUP \
    --description "YACHAQ-LEX Scraper Security Group" \
    --region $AWS_REGION 2>/dev/null || echo "Security group exists"

# Allow SSH
aws ec2 authorize-security-group-ingress \
    --group-name $SECURITY_GROUP \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region $AWS_REGION 2>/dev/null || echo "SSH rule exists"

# Create key pair if not exists
if [ ! -f ~/.ssh/${EC2_KEY_NAME}.pem ]; then
    echo "Creating EC2 key pair..."
    aws ec2 create-key-pair \
        --key-name $EC2_KEY_NAME \
        --query 'KeyMaterial' \
        --output text \
        --region $AWS_REGION > ~/.ssh/${EC2_KEY_NAME}.pem
    chmod 400 ~/.ssh/${EC2_KEY_NAME}.pem
fi

# Launch EC2 instance
echo "Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $EC2_KEY_NAME \
    --security-groups $SECURITY_GROUP \
    --region $AWS_REGION \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=yachaq-scraper}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance ID: $INSTANCE_ID"
echo "Waiting for instance to start..."

aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $AWS_REGION

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text \
    --region $AWS_REGION)

echo "Instance running at: $PUBLIC_IP"
echo "Waiting 30s for SSH to be ready..."
sleep 30

# Create setup script
cat > /tmp/setup_scraper.sh << 'EOF'
#!/bin/bash
set -e

echo "Installing dependencies..."
sudo yum update -y
sudo yum install -y python3 python3-pip git

echo "Installing Python packages..."
pip3 install requests beautifulsoup4 lxml scrapy boto3

echo "Creating scraper directory..."
mkdir -p ~/yachaq-scraper
cd ~/yachaq-scraper

echo "Setup complete!"
EOF

# Copy files to EC2
echo "Copying files to EC2..."
scp -i ~/.ssh/${EC2_KEY_NAME}.pem -o StrictHostKeyChecking=no \
    /tmp/setup_scraper.sh ec2-user@${PUBLIC_IP}:~/

scp -i ~/.ssh/${EC2_KEY_NAME}.pem -o StrictHostKeyChecking=no \
    rag/ingest/*.py ec2-user@${PUBLIC_IP}:~/yachaq-scraper/

# Run setup
echo "Running setup on EC2..."
ssh -i ~/.ssh/${EC2_KEY_NAME}.pem -o StrictHostKeyChecking=no \
    ec2-user@${PUBLIC_IP} 'bash ~/setup_scraper.sh'

echo ""
echo "=========================================="
echo "DEPLOYMENT COMPLETE"
echo "=========================================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo ""
echo "To connect:"
echo "  ssh -i ~/.ssh/${EC2_KEY_NAME}.pem ec2-user@${PUBLIC_IP}"
echo ""
echo "To start scraping:"
echo "  ssh -i ~/.ssh/${EC2_KEY_NAME}.pem ec2-user@${PUBLIC_IP}"
echo "  cd ~/yachaq-scraper"
echo "  python3 scrape_all.py"
echo ""
echo "To download results:"
echo "  scp -i ~/.ssh/${EC2_KEY_NAME}.pem -r ec2-user@${PUBLIC_IP}:~/yachaq-scraper/downloads ."
echo "=========================================="

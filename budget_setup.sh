#!/bin/bash

# Launch g5.4xlarge for Qwen2.5-Coder-14B
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type g5.4xlarge \
  --key-name your-key \
  --security-group-ids sg-your-sg \
  --user-data '#!/bin/bash
apt update && apt install -y docker.io nvidia-docker2
systemctl restart docker

# Run Qwen2.5-Coder-14B with vLLM
docker run -d --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-Coder-14B-Instruct \
  --host 0.0.0.0 --port 8000
'

echo "Launching $870/month server..."
echo "Use endpoint: http://INSTANCE-IP:8000/v1/chat/completions"
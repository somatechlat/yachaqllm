#!/bin/bash

# Launch g5.12xlarge instance
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --instance-type g5.12xlarge \
  --key-name your-key \
  --security-group-ids sg-your-sg \
  --subnet-id subnet-your-subnet \
  --user-data '#!/bin/bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update && apt-get install -y nvidia-container-toolkit
systemctl restart docker

# Run Qwen2.5-Coder with vLLM (OpenAI compatible)
docker run -d --gpus all \
  -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-Coder-32B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 4
'

echo "Instance launching... Check AWS console for IP address"
echo "Once running, use: http://YOUR-INSTANCE-IP:8000/v1/chat/completions"
provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "yachaq_lex_server" {
  ami           = "ami-0aa7d40eeae50c9a9" # Ubuntu 22.04 LTS
  instance_type = "t2.micro"
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.yachaq_lex_sg.id]
  iam_instance_profile = aws_iam_instance_profile.s3_access_profile.name

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y docker.io
              sudo systemctl start docker
              sudo systemctl enable docker
              sudo usermod -a -G docker ubuntu
              sudo apt-get install -y git
              git clone "YOUR_GIT_REPOSITORY_URL" /home/ubuntu/YACHAQ-LEX_full
              cd /home/ubuntu/YACHAQ-LEX_full
              pip install -r rag/app/requirements.txt
              EOF

  tags = {
    Name = "YACHAQ-LEX-Server"
  }
}

resource "aws_security_group" "yachaq_lex_sg" {
  name        = "yachaq-lex-sg"
  description = "Allow SSH and App traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "s3_access_role" {
  name = "yachaq-lex-s3-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_policy_attach" {
  role       = aws_iam_role.s3_access_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_instance_profile" "s3_access_profile" {
  name = "yachaq-lex-s3-access-profile"
  role = aws_iam_role.s3_access_role.name
}

resource "aws_s3_bucket" "yachaq_lex_data" {
  bucket = "yachaq-lex-data-bucket-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "YACHAQ-LEX-Data"
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 8
}

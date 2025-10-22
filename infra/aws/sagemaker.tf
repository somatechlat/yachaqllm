# SageMaker Execution Role
resource "aws_iam_role" "sagemaker_execution_role" {
  name = "yachaq-lex-sagemaker-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
}

# Attach SageMaker execution policy
resource "aws_iam_role_policy_attachment" "sagemaker_execution_policy" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

# S3 access for SageMaker
resource "aws_iam_role_policy_attachment" "sagemaker_s3_policy" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# Training data S3 bucket
resource "aws_s3_bucket" "yachaq_training_data" {
  bucket = "yachaq-lex-training-${random_id.bucket_suffix.hex}"
  
  tags = {
    Name = "YACHAQ-LEX-Training-Data"
  }
}

# Model artifacts S3 bucket
resource "aws_s3_bucket" "yachaq_model_artifacts" {
  bucket = "yachaq-lex-models-${random_id.bucket_suffix.hex}"
  
  tags = {
    Name = "YACHAQ-LEX-Model-Artifacts"
  }
}

# SageMaker Training Job (template) - DISABLED TO AVOID CHARGES
# Uncomment when ready to train the model
# resource "aws_sagemaker_training_job" "yachaq_lex_training" {
#   count = var.enable_training_job ? 1 : 0
#   
#   name     = "yachaq-lex-training-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
#   role_arn = aws_iam_role.sagemaker_execution_role.arn
#
#   algorithm_specification {
#     training_image = "763104351884.dkr.ecr.${var.aws_region}.amazonaws.com/pytorch-training:2.0.1-gpu-py310-cu118-ubuntu20.04-sagemaker"
#     training_input_mode = "File"
#   }
#
#   input_data_config {
#     channel_name = "training"
#     data_source {
#       s3_data_source {
#         s3_data_type = "S3Prefix"
#         s3_uri = "s3://${aws_s3_bucket.yachaq_training_data.bucket}/data/"
#         s3_data_distribution_type = "FullyReplicated"
#       }
#     }
#   }
#
#   output_data_config {
#     s3_output_path = "s3://${aws_s3_bucket.yachaq_model_artifacts.bucket}/output/"
#   }
#
#   resource_config {
#     instance_type   = var.training_instance_type
#     instance_count  = 1
#     volume_size_in_gb = 30
#   }
#
#   stopping_condition {
#     max_runtime_in_seconds = 86400  # 24 hours
#   }
#
#   hyperparameters = {
#     epochs = "3"
#     batch_size = "4"
#     learning_rate = "0.0001"
#   }
#
#   tags = {
#     Name = "YACHAQ-LEX-Training"
#   }
# }
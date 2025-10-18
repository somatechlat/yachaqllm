variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "key_name" {
  description = "Name of the EC2 Key Pair to use for SSH access."
  type        = string
  default     = "yachaq-lex-key"
}

output "instance_public_ip" {
  description = "Public IP address of the YACHAQ-LEX server."
  value       = aws_instance.yachaq_lex_server.public_ip
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for YACHAQ-LEX data."
  value       = aws_s3_bucket.yachaq_lex_data.bucket
}

# Secrets Policy

- **AWS Credentials:** AWS credentials should never be stored in the repository. For local development, use environment variables. For production, use the IAM Role attached to the EC2 instance.
- **API Keys:** Any third-party API keys should be stored in a secure secrets management system.

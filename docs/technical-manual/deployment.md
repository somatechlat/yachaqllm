# Deployment

YACHAQ-LEX is deployed using Terraform and Docker.

- **Infrastructure:** The `infra/aws` directory contains Terraform scripts to provision an EC2 instance, S3 bucket, and all necessary security groups and IAM roles.
- **Application:** The `docker` directory contains a `compose.rag.yaml` file to build and run the FastAPI application and Qdrant database in Docker containers.

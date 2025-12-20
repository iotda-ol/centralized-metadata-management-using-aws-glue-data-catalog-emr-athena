"""
Main Terraform configuration for dev environment
"""

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    # Backend configuration should be provided via backend config file
    # Example: terraform init -backend-config=backend.conf
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Owner       = "data-engineering"
  }
}

# Get AWS account ID
data "aws_caller_identity" "current" {}

# KMS key for encryption
resource "aws_kms_key" "main" {
  description             = "${var.project_name}-${var.environment}-key"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = local.common_tags
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.project_name}-${var.environment}"
  target_key_id = aws_kms_key.main.key_id
}

# S3 Module
module "s3" {
  source = "../../modules/s3"

  project_name = var.project_name
  environment  = var.environment
  account_id   = data.aws_caller_identity.current.account_id
  kms_key_arn  = aws_kms_key.main.arn
  common_tags  = local.common_tags
}

# IAM Module
module "iam" {
  source = "../../modules/iam"

  project_name         = var.project_name
  environment          = var.environment
  data_lake_bucket_arn = module.s3.data_lake_bucket_arn
  scripts_bucket_arn   = module.s3.scripts_bucket_arn
  common_tags          = local.common_tags
}

# Glue Module
module "glue" {
  source = "../../modules/glue"

  project_name  = var.project_name
  environment   = var.environment
  glue_role_arn = module.iam.glue_role_arn
  kms_key_arn   = aws_kms_key.main.arn
  common_tags   = local.common_tags

  databases = var.glue_databases
  crawlers  = var.glue_crawlers
}

# Athena Module
module "athena" {
  source = "../../modules/athena"

  project_name          = var.project_name
  environment           = var.environment
  results_bucket_name   = module.s3.athena_results_bucket_name
  bytes_scanned_cutoff  = var.athena_bytes_scanned_cutoff
  common_tags           = local.common_tags
}

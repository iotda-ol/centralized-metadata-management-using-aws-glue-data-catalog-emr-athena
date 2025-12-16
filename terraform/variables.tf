variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "centralized-metadata"
}

variable "glue_database_name" {
  description = "Name of the Glue Data Catalog database"
  type        = string
  default     = "centralized_metadata_db"
}

variable "hive_metastore_uri" {
  description = "URI of the existing Hive metastore (optional, for migration)"
  type        = string
  default     = ""
}

variable "hive_metastore_username" {
  description = "Username for Hive metastore connection"
  type        = string
  default     = ""
  sensitive   = true
}

variable "hive_metastore_password" {
  description = "Password for Hive metastore connection"
  type        = string
  default     = ""
  sensitive   = true
}

variable "s3_data_bucket_name" {
  description = "S3 bucket name for data storage"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$", var.s3_data_bucket_name))
    error_message = "S3 bucket name must be lowercase, between 3-63 characters, start and end with a letter or number, and contain only letters, numbers, and hyphens."
  }
}

variable "s3_athena_results_bucket_name" {
  description = "S3 bucket name for Athena query results"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$", var.s3_athena_results_bucket_name))
    error_message = "S3 bucket name must be lowercase, between 3-63 characters, start and end with a letter or number, and contain only letters, numbers, and hyphens."
  }
}

variable "enable_crawler" {
  description = "Enable Glue crawler for automatic schema discovery"
  type        = bool
  default     = true
}

variable "crawler_schedule" {
  description = "Cron expression for crawler schedule"
  type        = string
  default     = "cron(0 2 * * ? *)" # Daily at 2 AM UTC
}

variable "cloudwatch_log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 7

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653], var.cloudwatch_log_retention_days)
    error_message = "CloudWatch log retention must be one of the allowed values: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653 days."
  }
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

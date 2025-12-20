variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "metadata-mgmt"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "glue_databases" {
  description = "Glue databases to create"
  type = map(object({
    description = string
  }))
  default = {
    raw_data = {
      description = "Raw ingested data"
    }
    processed_data = {
      description = "Processed and cleaned data"
    }
    analytics = {
      description = "Analytics-ready data"
    }
  }
}

variable "glue_crawlers" {
  description = "Glue crawlers to create"
  type = map(object({
    database        = string
    s3_targets      = list(string)
    delete_behavior = string
    update_behavior = string
    schedule        = optional(string)
  }))
  default = {}
}

variable "athena_bytes_scanned_cutoff" {
  description = "Athena bytes scanned cutoff per query"
  type        = number
  default     = 10737418240  # 10 GB
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "databases" {
  description = "Map of Glue databases to create"
  type = map(object({
    description = string
  }))
  default = {}
}

variable "crawlers" {
  description = "Map of Glue crawlers to create"
  type = map(object({
    database        = string
    s3_targets      = list(string)
    delete_behavior = string
    update_behavior = string
    schedule        = optional(string)
  }))
  default = {}
}

variable "connections" {
  description = "Map of Glue connections to create"
  type = map(object({
    properties          = map(string)
    availability_zone   = string
    security_group_ids  = list(string)
    subnet_id           = string
  }))
  default = {}
}

variable "glue_role_arn" {
  description = "ARN of the IAM role for Glue"
  type        = string
}

variable "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

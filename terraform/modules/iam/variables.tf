variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "data_lake_bucket_arn" {
  description = "ARN of the data lake bucket"
  type        = string
}

variable "scripts_bucket_arn" {
  description = "ARN of the scripts bucket"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply"
  type        = map(string)
  default     = {}
}

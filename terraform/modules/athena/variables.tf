variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "results_bucket_name" {
  description = "S3 bucket for query results"
  type        = string
}

variable "bytes_scanned_cutoff" {
  description = "Maximum bytes scanned per query (0 for unlimited)"
  type        = number
  default     = 10737418240  # 10 GB
}

variable "common_tags" {
  description = "Common tags to apply"
  type        = map(string)
  default     = {}
}

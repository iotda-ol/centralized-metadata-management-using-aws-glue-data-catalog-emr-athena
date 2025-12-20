variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "emr_release_label" {
  description = "EMR release version"
  type        = string
  default     = "emr-6.9.0"
}

variable "applications" {
  description = "List of applications to install"
  type        = list(string)
  default     = ["Hadoop", "Hive", "Spark", "Livy", "JupyterHub"]
}

variable "service_role_arn" {
  description = "ARN of the EMR service role"
  type        = string
}

variable "instance_profile_arn" {
  description = "ARN of the EC2 instance profile"
  type        = string
}

variable "master_security_group_id" {
  description = "Security group ID for master node"
  type        = string
}

variable "slave_security_group_id" {
  description = "Security group ID for slave nodes"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for EMR cluster"
  type        = string
}

variable "key_name" {
  description = "EC2 key pair name"
  type        = string
  default     = null
}

variable "master_instance_type" {
  description = "Instance type for master node"
  type        = string
  default     = "m5.xlarge"
}

variable "master_ebs_size" {
  description = "EBS volume size for master node (GB)"
  type        = number
  default     = 100
}

variable "core_instance_type" {
  description = "Instance type for core nodes"
  type        = string
  default     = "m5.xlarge"
}

variable "core_instance_count" {
  description = "Number of core instances"
  type        = number
  default     = 2
}

variable "core_max_instance_count" {
  description = "Maximum number of core instances for autoscaling"
  type        = number
  default     = 10
}

variable "core_ebs_size" {
  description = "EBS volume size for core nodes (GB)"
  type        = number
  default     = 100
}

variable "enable_autoscaling" {
  description = "Enable autoscaling for core nodes"
  type        = bool
  default     = true
}

variable "bootstrap_actions" {
  description = "List of bootstrap actions"
  type = list(object({
    name = string
    path = string
    args = optional(list(string))
  }))
  default = []
}

variable "log_uri" {
  description = "S3 URI for EMR logs"
  type        = string
}

variable "termination_protection" {
  description = "Enable termination protection"
  type        = bool
  default     = false
}

variable "keep_alive" {
  description = "Keep cluster alive when no steps"
  type        = bool
  default     = true
}

variable "common_tags" {
  description = "Common tags to apply"
  type        = map(string)
  default     = {}
}

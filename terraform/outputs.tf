output "glue_database_name" {
  description = "Name of the Glue Data Catalog database"
  value       = aws_glue_catalog_database.main.name
}

output "glue_database_arn" {
  description = "ARN of the Glue Data Catalog database"
  value       = aws_glue_catalog_database.main.arn
}

output "glue_service_role_arn" {
  description = "ARN of the Glue service IAM role"
  value       = aws_iam_role.glue_service_role.arn
}

output "glue_service_role_name" {
  description = "Name of the Glue service IAM role"
  value       = aws_iam_role.glue_service_role.name
}

output "emr_service_role_arn" {
  description = "ARN of the EMR service IAM role"
  value       = aws_iam_role.emr_service_role.arn
}

output "emr_ec2_role_arn" {
  description = "ARN of the EMR EC2 IAM role"
  value       = aws_iam_role.emr_ec2_role.arn
}

output "emr_ec2_instance_profile_arn" {
  description = "ARN of the EMR EC2 instance profile"
  value       = aws_iam_instance_profile.emr_ec2_instance_profile.arn
}

output "emr_ec2_instance_profile_name" {
  description = "Name of the EMR EC2 instance profile"
  value       = aws_iam_instance_profile.emr_ec2_instance_profile.name
}

output "athena_execution_role_arn" {
  description = "ARN of the Athena execution IAM role"
  value       = aws_iam_role.athena_execution_role.arn
}

output "athena_workgroup_name" {
  description = "Name of the Athena workgroup"
  value       = aws_athena_workgroup.main.name
}

output "athena_workgroup_arn" {
  description = "ARN of the Athena workgroup"
  value       = aws_athena_workgroup.main.arn
}

output "data_bucket_name" {
  description = "Name of the S3 data bucket"
  value       = aws_s3_bucket.data_bucket.bucket
}

output "data_bucket_arn" {
  description = "ARN of the S3 data bucket"
  value       = aws_s3_bucket.data_bucket.arn
}

output "athena_results_bucket_name" {
  description = "Name of the Athena results S3 bucket"
  value       = aws_s3_bucket.athena_results_bucket.bucket
}

output "athena_results_bucket_arn" {
  description = "ARN of the Athena results S3 bucket"
  value       = aws_s3_bucket.athena_results_bucket.arn
}

output "glue_crawler_name" {
  description = "Name of the Glue crawler (if enabled)"
  value       = var.enable_crawler ? aws_glue_crawler.data_crawler[0].name : null
}

output "glue_crawler_arn" {
  description = "ARN of the Glue crawler (if enabled)"
  value       = var.enable_crawler ? aws_glue_crawler.data_crawler[0].arn : null
}

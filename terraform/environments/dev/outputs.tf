output "data_lake_bucket_name" {
  description = "Name of the data lake S3 bucket"
  value       = module.s3.data_lake_bucket_name
}

output "scripts_bucket_name" {
  description = "Name of the scripts S3 bucket"
  value       = module.s3.scripts_bucket_name
}

output "athena_results_bucket_name" {
  description = "Name of the Athena results S3 bucket"
  value       = module.s3.athena_results_bucket_name
}

output "glue_databases" {
  description = "Names of created Glue databases"
  value       = module.glue.database_names
}

output "glue_role_arn" {
  description = "ARN of the Glue service role"
  value       = module.iam.glue_role_arn
}

output "athena_workgroup" {
  description = "Name of the primary Athena workgroup"
  value       = module.athena.primary_workgroup_name
}

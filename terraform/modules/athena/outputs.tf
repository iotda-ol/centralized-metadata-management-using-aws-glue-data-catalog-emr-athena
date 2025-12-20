output "primary_workgroup_name" {
  description = "Name of the primary Athena workgroup"
  value       = aws_athena_workgroup.main.name
}

output "analytics_workgroup_name" {
  description = "Name of the analytics Athena workgroup"
  value       = aws_athena_workgroup.analytics.name
}

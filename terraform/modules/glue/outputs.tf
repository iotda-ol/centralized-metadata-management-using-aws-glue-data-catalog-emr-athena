output "database_names" {
  description = "Names of created Glue databases"
  value       = { for k, v in aws_glue_catalog_database.main : k => v.name }
}

output "crawler_names" {
  description = "Names of created Glue crawlers"
  value       = { for k, v in aws_glue_crawler.main : k => v.name }
}

output "security_configuration_name" {
  description = "Name of the Glue security configuration"
  value       = aws_glue_security_configuration.main.name
}

output "connection_names" {
  description = "Names of created Glue connections"
  value       = { for k, v in aws_glue_connection.main : k => v.name }
}

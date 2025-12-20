output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "emr_master_security_group_id" {
  description = "EMR master security group ID"
  value       = aws_security_group.emr_master.id
}

output "emr_slave_security_group_id" {
  description = "EMR slave security group ID"
  value       = aws_security_group.emr_slave.id
}

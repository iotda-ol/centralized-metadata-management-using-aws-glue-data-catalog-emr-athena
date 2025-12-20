output "cluster_id" {
  description = "EMR cluster ID"
  value       = aws_emr_cluster.main.id
}

output "cluster_name" {
  description = "EMR cluster name"
  value       = aws_emr_cluster.main.name
}

output "master_public_dns" {
  description = "Master node public DNS"
  value       = aws_emr_cluster.main.master_public_dns
}

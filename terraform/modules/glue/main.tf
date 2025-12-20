/**
 * AWS Glue Data Catalog Module
 * Creates and manages Glue databases, tables, crawlers, and configurations
 */

# Glue Catalog Database
resource "aws_glue_catalog_database" "main" {
  for_each = var.databases

  name        = "${var.project_name}-${var.environment}-${each.key}"
  description = each.value.description

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-${each.key}"
      Database    = each.key
      Environment = var.environment
    }
  )
}

# Glue Crawler for automatic schema discovery
resource "aws_glue_crawler" "main" {
  for_each = var.crawlers

  name          = "${var.project_name}-${var.environment}-${each.key}-crawler"
  database_name = aws_glue_catalog_database.main[each.value.database].name
  role          = var.glue_role_arn

  dynamic "s3_target" {
    for_each = each.value.s3_targets
    content {
      path = s3_target.value
    }
  }

  schema_change_policy {
    delete_behavior = each.value.delete_behavior
    update_behavior = each.value.update_behavior
  }

  configuration = jsonencode({
    Version = 1.0
    CrawlerOutput = {
      Partitions = { AddOrUpdateBehavior = "InheritFromTable" }
    }
  })

  schedule = lookup(each.value, "schedule", null)

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-${each.key}-crawler"
      Environment = var.environment
    }
  )
}

# Glue Security Configuration
resource "aws_glue_security_configuration" "main" {
  name = "${var.project_name}-${var.environment}-security-config"

  encryption_configuration {
    cloudwatch_encryption {
      cloudwatch_encryption_mode = "SSE-KMS"
      kms_key_arn                = var.kms_key_arn
    }

    job_bookmarks_encryption {
      job_bookmarks_encryption_mode = "CSE-KMS"
      kms_key_arn                   = var.kms_key_arn
    }

    s3_encryption {
      s3_encryption_mode = "SSE-KMS"
      kms_key_arn        = var.kms_key_arn
    }
  }
}

# Glue Connection (for JDBC sources if needed)
resource "aws_glue_connection" "main" {
  for_each = var.connections

  name = "${var.project_name}-${var.environment}-${each.key}"

  connection_properties = each.value.properties

  physical_connection_requirements {
    availability_zone      = each.value.availability_zone
    security_group_id_list = each.value.security_group_ids
    subnet_id              = each.value.subnet_id
  }

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-${each.key}"
      Environment = var.environment
    }
  )
}

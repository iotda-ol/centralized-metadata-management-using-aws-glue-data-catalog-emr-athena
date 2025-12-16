# S3 Bucket for data storage
resource "aws_s3_bucket" "data_bucket" {
  bucket = var.s3_data_bucket_name

  tags = merge(var.tags, {
    Name = "${var.project_name}-data-bucket"
  })
}

# Enable versioning for data bucket
resource "aws_s3_bucket_versioning" "data_bucket_versioning" {
  bucket = aws_s3_bucket.data_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket for Athena query results
resource "aws_s3_bucket" "athena_results_bucket" {
  bucket = var.s3_athena_results_bucket_name

  tags = merge(var.tags, {
    Name = "${var.project_name}-athena-results-bucket"
  })
}

# Enable versioning for Athena results bucket
resource "aws_s3_bucket_versioning" "athena_results_bucket_versioning" {
  bucket = aws_s3_bucket.athena_results_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# AWS Glue Data Catalog Database
resource "aws_glue_catalog_database" "main" {
  name        = var.glue_database_name
  description = "Centralized metadata database for EMR and Athena"

  tags = merge(var.tags, {
    Name = "${var.project_name}-glue-database"
  })
}

# AWS Glue Connection for Hive Metastore (if URI is provided)
resource "aws_glue_connection" "hive_metastore" {
  count = var.hive_metastore_uri != "" ? 1 : 0

  name = "${var.project_name}-hive-metastore-connection"

  connection_properties = {
    JDBC_CONNECTION_URL = var.hive_metastore_uri
    USERNAME            = var.hive_metastore_username
    PASSWORD            = var.hive_metastore_password
  }

  physical_connection_requirements {
    security_group_id_list = []
    availability_zone      = ""
    subnet_id              = ""
  }
}

# AWS Glue Crawler for automatic schema discovery
resource "aws_glue_crawler" "data_crawler" {
  count = var.enable_crawler ? 1 : 0

  name          = "${var.project_name}-data-crawler-${var.environment}"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.main.name

  s3_target {
    path = "s3://${aws_s3_bucket.data_bucket.bucket}/"
  }

  schedule = var.crawler_schedule

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  configuration = jsonencode({
    Version = 1.0
    CrawlerOutput = {
      Partitions = { AddOrUpdateBehavior = "InheritFromTable" }
    }
  })

  tags = merge(var.tags, {
    Name = "${var.project_name}-glue-crawler"
  })
}

# Athena Workgroup for query execution
resource "aws_athena_workgroup" "main" {
  name = "${var.project_name}-workgroup-${var.environment}"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results_bucket.bucket}/results/"

      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }

  tags = merge(var.tags, {
    Name = "${var.project_name}-athena-workgroup"
  })
}

# CloudWatch Log Group for Glue jobs
resource "aws_cloudwatch_log_group" "glue_logs" {
  name              = "/aws/glue/${var.project_name}"
  retention_in_days = 7

  tags = merge(var.tags, {
    Name = "${var.project_name}-glue-logs"
  })
}

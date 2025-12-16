# IAM Role for AWS Glue Service
resource "aws_iam_role" "glue_service_role" {
  name = "${var.project_name}-glue-service-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.project_name}-glue-service-role"
  })
}

# Attach AWS managed policy for Glue service
resource "aws_iam_role_policy_attachment" "glue_service_policy" {
  role       = aws_iam_role.glue_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Custom policy for S3 access
resource "aws_iam_role_policy" "glue_s3_policy" {
  name = "${var.project_name}-glue-s3-policy"
  role = aws_iam_role.glue_service_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_data_bucket_name}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_data_bucket_name}"
        ]
      }
    ]
  })
}

# IAM Role for Amazon EMR
resource "aws_iam_role" "emr_service_role" {
  name = "${var.project_name}-emr-service-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "elasticmapreduce.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.project_name}-emr-service-role"
  })
}

# Attach EMR service policy
resource "aws_iam_role_policy_attachment" "emr_service_policy" {
  role       = aws_iam_role.emr_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceRole"
}

# IAM Role for EMR EC2 instances
resource "aws_iam_role" "emr_ec2_role" {
  name = "${var.project_name}-emr-ec2-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.project_name}-emr-ec2-role"
  })
}

# Instance profile for EMR EC2 instances
resource "aws_iam_instance_profile" "emr_ec2_instance_profile" {
  name = "${var.project_name}-emr-ec2-instance-profile-${var.environment}"
  role = aws_iam_role.emr_ec2_role.name
}

# Attach EMR EC2 instance profile policy
resource "aws_iam_role_policy_attachment" "emr_ec2_policy" {
  role       = aws_iam_role.emr_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceforEC2Role"
}

# Custom policy for EMR to access Glue Data Catalog
resource "aws_iam_role_policy" "emr_glue_catalog_policy" {
  name = "${var.project_name}-emr-glue-catalog-policy"
  role = aws_iam_role.emr_ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartition",
          "glue:GetPartitions",
          "glue:CreateTable",
          "glue:UpdateTable",
          "glue:DeleteTable",
          "glue:CreatePartition",
          "glue:UpdatePartition",
          "glue:DeletePartition",
          "glue:BatchCreatePartition",
          "glue:BatchDeletePartition",
          "glue:BatchUpdatePartition"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM Role for Athena
resource "aws_iam_role" "athena_execution_role" {
  name = "${var.project_name}-athena-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "athena.amazonaws.com"
        }
      },
      # Note: In production, restrict this to specific IAM users/roles
      # that need to execute Athena queries, rather than the entire account
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Condition = {
          StringEquals = {
            "sts:ExternalId" = "athena-execution"
          }
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.project_name}-athena-execution-role"
  })
}

# Custom policy for Athena to access Glue Data Catalog and S3
resource "aws_iam_role_policy" "athena_glue_s3_policy" {
  name = "${var.project_name}-athena-glue-s3-policy"
  role = aws_iam_role.athena_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartition",
          "glue:GetPartitions"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_data_bucket_name}",
          "arn:aws:s3:::${var.s3_data_bucket_name}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_athena_results_bucket_name}",
          "arn:aws:s3:::${var.s3_athena_results_bucket_name}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "athena:StartQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:StopQueryExecution",
          "athena:GetWorkGroup"
        ]
        Resource = "*"
      }
    ]
  })
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Deployment Guide

This guide provides step-by-step instructions for deploying the centralized metadata management solution using AWS Glue Data Catalog.

## Prerequisites

### Required Tools
- **Terraform** (>= 1.0): [Install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- **AWS CLI** (>= 2.0): [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **Python** (>= 3.8): For Hive import script
- **Git**: For cloning the repository

### AWS Requirements
- AWS Account with appropriate permissions
- IAM user or role with permissions to create:
  - IAM roles and policies
  - S3 buckets
  - Glue resources (databases, crawlers, connections)
  - Athena workgroups
  - CloudWatch log groups

### Minimum IAM Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:CreatePolicy",
        "iam:AttachRolePolicy",
        "iam:PassRole",
        "s3:CreateBucket",
        "s3:PutBucketVersioning",
        "glue:CreateDatabase",
        "glue:CreateCrawler",
        "glue:CreateConnection",
        "athena:CreateWorkGroup",
        "logs:CreateLogGroup"
      ],
      "Resource": "*"
    }
  ]
}
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/centralized-metadata-management-using-aws-glue-data-catalog-emr-athena.git
cd centralized-metadata-management-using-aws-glue-data-catalog-emr-athena
```

### 2. Configure AWS Credentials

```bash
# Option 1: Configure AWS CLI
aws configure

# Option 2: Use environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Option 3: Use AWS SSO
aws sso login --profile your-profile
export AWS_PROFILE=your-profile
```

### 3. Customize Configuration

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
```hcl
# AWS Configuration
aws_region  = "us-east-1"
environment = "dev"

# Project Configuration
project_name        = "centralized-metadata"
glue_database_name  = "centralized_metadata_db"

# S3 Configuration (use unique names)
s3_data_bucket_name            = "your-org-metadata-data-dev-12345"
s3_athena_results_bucket_name  = "your-org-metadata-athena-dev-12345"

# Glue Crawler
enable_crawler   = true
crawler_schedule = "cron(0 2 * * ? *)"

# Tags
tags = {
  Owner      = "DataEngineering"
  CostCenter = "Analytics"
}
```

### 4. Initialize and Deploy with Terraform

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy infrastructure
terraform apply

# Confirm by typing 'yes' when prompted
```

**Expected Output**:
```
Apply complete! Resources: 15 added, 0 changed, 0 destroyed.

Outputs:

athena_workgroup_name = "centralized-metadata-workgroup-dev"
data_bucket_name = "your-org-metadata-data-dev-12345"
glue_database_name = "centralized_metadata_db"
...
```

### 5. Verify Deployment

```bash
# Verify Glue Database
aws glue get-database --name centralized_metadata_db

# Verify Crawler (if enabled)
aws glue get-crawler --name centralized-metadata-data-crawler-dev

# Verify S3 Buckets
aws s3 ls | grep metadata

# Verify IAM Roles
aws iam get-role --role-name centralized-metadata-glue-service-role-dev
```

## Detailed Deployment Steps

### Phase 1: Infrastructure Setup

#### Step 1: Review Terraform Configuration

Examine the Terraform files:
```bash
terraform/
├── provider.tf      # AWS provider configuration
├── variables.tf     # Input variables
├── main.tf          # Core resources (S3, Glue, Athena)
├── iam.tf          # IAM roles and policies
├── outputs.tf      # Output values
└── terraform.tfvars # Your custom values
```

#### Step 2: Validate Configuration

```bash
cd terraform

# Validate syntax
terraform validate

# Check formatting
terraform fmt -check

# Generate and review plan
terraform plan -out=tfplan
```

#### Step 3: Deploy Infrastructure

```bash
# Apply the plan
terraform apply tfplan

# Or apply directly (requires confirmation)
terraform apply
```

#### Step 4: Save Outputs

```bash
# Save outputs to file
terraform output -json > ../outputs.json

# View specific output
terraform output glue_database_name
```

### Phase 2: Data Upload and Schema Discovery

#### Step 1: Upload Sample Data

```bash
# Get bucket name from Terraform output
DATA_BUCKET=$(terraform output -raw data_bucket_name)

# Upload sample data
aws s3 cp sample-data/ s3://${DATA_BUCKET}/data/ --recursive

# Or create sample data structure
aws s3 cp example.csv s3://${DATA_BUCKET}/data/sales/year=2024/month=01/
```

#### Step 2: Run Glue Crawler

```bash
# Get crawler name
CRAWLER_NAME=$(terraform output -raw glue_crawler_name)

# Start crawler manually
aws glue start-crawler --name ${CRAWLER_NAME}

# Check crawler status
aws glue get-crawler --name ${CRAWLER_NAME} --query 'Crawler.State'

# Wait for completion (status: READY)
aws glue get-crawler --name ${CRAWLER_NAME} --query 'Crawler.LastCrawl'
```

#### Step 3: Verify Tables

```bash
# List tables in database
aws glue get-tables --database-name centralized_metadata_db \
  --query 'TableList[*].Name'

# Get table details
aws glue get-table --database-name centralized_metadata_db \
  --name sales --query 'Table.StorageDescriptor'
```

### Phase 3: EMR Integration

#### Step 1: Create EMR Cluster Configuration

Create `emr-config.json`:
```json
[
  {
    "Classification": "hive-site",
    "Properties": {
      "hive.metastore.client.factory.class": "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
    }
  },
  {
    "Classification": "spark-hive-site",
    "Properties": {
      "hive.metastore.client.factory.class": "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
    }
  }
]
```

#### Step 2: Launch EMR Cluster

```bash
# Get IAM role ARNs
EMR_SERVICE_ROLE=$(terraform output -raw emr_service_role_arn)
EMR_INSTANCE_PROFILE=$(terraform output -raw emr_ec2_instance_profile_name)

# Create EMR cluster
aws emr create-cluster \
  --name "EMR-Glue-Catalog" \
  --release-label emr-6.10.0 \
  --applications Name=Spark Name=Hive Name=Presto \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --service-role ${EMR_SERVICE_ROLE} \
  --ec2-attributes InstanceProfile=${EMR_INSTANCE_PROFILE},KeyName=your-key \
  --configurations file://emr-config.json \
  --log-uri s3://${DATA_BUCKET}/emr-logs/
```

#### Step 3: Test EMR with Glue Catalog

SSH into EMR master node and run:
```bash
# Start Hive CLI
hive

# Test queries
SHOW DATABASES;
USE centralized_metadata_db;
SHOW TABLES;
SELECT * FROM sales LIMIT 10;
```

### Phase 4: Athena Integration

#### Step 1: Configure Athena Workgroup

```bash
# Get workgroup name
WORKGROUP=$(terraform output -raw athena_workgroup_name)

# Verify workgroup
aws athena get-work-group --work-group ${WORKGROUP}
```

#### Step 2: Run Test Queries

Using AWS Console:
1. Navigate to Amazon Athena
2. Select workgroup: `centralized-metadata-workgroup-dev`
3. Select database: `centralized_metadata_db`
4. Run query:
```sql
SELECT * FROM sales LIMIT 10;
```

Using AWS CLI:
```bash
# Get results bucket
RESULTS_BUCKET=$(terraform output -raw athena_results_bucket_name)

# Execute query
QUERY_ID=$(aws athena start-query-execution \
  --query-string "SELECT * FROM sales LIMIT 10" \
  --query-execution-context Database=centralized_metadata_db \
  --result-configuration OutputLocation=s3://${RESULTS_BUCKET}/results/ \
  --work-group ${WORKGROUP} \
  --query 'QueryExecutionId' --output text)

# Check status
aws athena get-query-execution --query-execution-id ${QUERY_ID} \
  --query 'QueryExecution.Status.State'

# Get results
aws athena get-query-results --query-execution-id ${QUERY_ID}
```

### Phase 5: Hive Metastore Migration (Optional)

If migrating from existing Hive metastore:

#### Step 1: Prepare Migration Script

```bash
cd scripts

# Install dependencies
pip install boto3 PyHive

# Configure script
export AWS_REGION="us-east-1"
export GLUE_DATABASE="centralized_metadata_db"
export HIVE_METASTORE_URI="jdbc:mysql://hive-host:3306/hive"
```

#### Step 2: Run Migration

```bash
python hive-import.py \
  --hive-uri ${HIVE_METASTORE_URI} \
  --hive-username hive_user \
  --hive-password your_password \
  --aws-region ${AWS_REGION} \
  --glue-database ${GLUE_DATABASE}
```

#### Step 3: Verify Migration

```bash
# Compare table counts
aws glue get-tables --database-name centralized_metadata_db \
  --query 'length(TableList)'

# Verify specific table
aws glue get-table --database-name centralized_metadata_db \
  --name your_table_name
```

## Post-Deployment Configuration

### 1. Set Up CloudWatch Alarms

```bash
# Create alarm for crawler failures
aws cloudwatch put-metric-alarm \
  --alarm-name glue-crawler-failures \
  --alarm-description "Alert on Glue crawler failures" \
  --metric-name FailedCrawlerRuns \
  --namespace AWS/Glue \
  --statistic Sum \
  --period 3600 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold
```

### 2. Configure Budget Alerts

```bash
# Create budget for Glue costs
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file://budget-config.json
```

### 3. Enable CloudTrail Logging

```bash
# Verify CloudTrail is enabled
aws cloudtrail describe-trails

# Create trail if needed
aws cloudtrail create-trail \
  --name glue-audit-trail \
  --s3-bucket-name your-cloudtrail-bucket
```

### 4. Set Up Backup Strategy

```bash
# Tag critical resources for backup
aws glue tag-resource \
  --resource-arn $(terraform output -raw glue_database_arn) \
  --tags-to-add Backup=daily
```

## Validation and Testing

### Test Checklist

- [ ] Glue database created successfully
- [ ] S3 buckets created and accessible
- [ ] IAM roles and policies configured
- [ ] Glue crawler runs successfully
- [ ] Tables discovered in catalog
- [ ] EMR cluster connects to Glue Catalog
- [ ] Hive queries work on EMR
- [ ] Athena queries execute successfully
- [ ] Permissions properly configured
- [ ] CloudWatch logs available

### Validation Scripts

```bash
# Run comprehensive validation
./scripts/validate-deployment.sh

# Test each component
terraform output -json | jq
aws glue get-tables --database-name centralized_metadata_db
aws athena list-work-groups
```

## Troubleshooting

### Common Issues

#### Issue: Terraform apply fails

**Error**: "BucketAlreadyExists"
```
Error: error creating S3 bucket: BucketAlreadyExists
```

**Solution**: S3 bucket names must be globally unique. Update `s3_data_bucket_name` in `terraform.tfvars` with a unique name.

#### Issue: Crawler fails to run

**Error**: "Access Denied to S3 bucket"

**Solution**:
```bash
# Verify IAM role has S3 access
aws iam get-role-policy \
  --role-name centralized-metadata-glue-service-role-dev \
  --policy-name centralized-metadata-glue-s3-policy

# Update policy if needed
terraform apply -target=aws_iam_role_policy.glue_s3_policy
```

#### Issue: EMR cluster can't access Glue Catalog

**Error**: "AccessDeniedException: User is not authorized"

**Solution**:
```bash
# Verify EMR instance profile
aws iam get-role-policy \
  --role-name centralized-metadata-emr-ec2-role-dev \
  --policy-name centralized-metadata-emr-glue-catalog-policy

# Attach required policy
terraform apply -target=aws_iam_role_policy.emr_glue_catalog_policy
```

#### Issue: Athena queries fail

**Error**: "Unable to verify/create output bucket"

**Solution**: Verify Athena results bucket exists and role has permissions:
```bash
aws s3 ls s3://$(terraform output -raw athena_results_bucket_name)/
```

## Cleanup

### Remove All Resources

```bash
cd terraform

# Destroy infrastructure
terraform destroy

# Confirm by typing 'yes'
```

### Manual Cleanup (if needed)

```bash
# Empty S3 buckets first
DATA_BUCKET=$(terraform output -raw data_bucket_name)
RESULTS_BUCKET=$(terraform output -raw athena_results_bucket_name)

aws s3 rm s3://${DATA_BUCKET} --recursive
aws s3 rm s3://${RESULTS_BUCKET} --recursive

# Then run terraform destroy
terraform destroy
```

## Next Steps

After successful deployment:

1. **Review Documentation**:
   - Read [ARCHITECTURE.md](ARCHITECTURE.md) for system overview
   - Study [HIVE_COMPATIBILITY.md](HIVE_COMPATIBILITY.md) for EMR integration
   - Review [DEA_C01_BEST_PRACTICES.md](DEA_C01_BEST_PRACTICES.md)

2. **Explore Examples**:
   - Check `examples/` directory for usage patterns
   - Try sample queries and workflows

3. **Customize for Your Needs**:
   - Adjust crawler schedule
   - Configure additional databases
   - Set up Lake Formation for fine-grained access control
   - Implement data quality checks

4. **Production Hardening**:
   - Enable MFA for administrative access
   - Set up cross-region replication for critical data
   - Implement comprehensive monitoring
   - Document runbooks for common operations

## Support and Resources

- **AWS Glue Documentation**: https://docs.aws.amazon.com/glue/
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/
- **AWS Support**: https://aws.amazon.com/support/
- **Community Forums**: https://forums.aws.amazon.com/

## Appendix

### A. Cost Estimation

**Monthly Costs** (approximate, for 1,000 tables, 10M requests):
- Glue Data Catalog storage: $10
- Glue API requests: $10
- S3 storage (100GB): $2.30
- Athena queries (100GB scanned): $5
- CloudWatch logs: $1
- **Total**: ~$28/month

### B. Terraform Commands Reference

```bash
# Initialize
terraform init

# Plan
terraform plan -out=tfplan

# Apply
terraform apply tfplan

# Destroy specific resource
terraform destroy -target=resource_type.resource_name

# Show state
terraform show

# List resources
terraform state list

# Import existing resource
terraform import aws_glue_catalog_database.main database_name

# Refresh state
terraform refresh

# Output values
terraform output

# Format code
terraform fmt -recursive
```

### C. AWS CLI Commands Reference

```bash
# Glue
aws glue get-databases
aws glue get-tables --database-name db_name
aws glue start-crawler --name crawler_name
aws glue get-crawler-metrics

# Athena
aws athena list-databases --catalog-name AwsDataCatalog
aws athena start-query-execution --query-string "SELECT 1"
aws athena get-query-execution --query-execution-id id

# S3
aws s3 ls s3://bucket-name/
aws s3 cp local-file s3://bucket-name/path/
aws s3 sync local-dir s3://bucket-name/path/

# IAM
aws iam list-roles
aws iam get-role --role-name role-name
aws iam list-role-policies --role-name role-name
```

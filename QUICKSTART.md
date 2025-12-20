# Quick Start Guide

This guide will help you get started with the Centralized Metadata Management solution in under 30 minutes.

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] AWS Account with admin access
- [ ] AWS CLI v2 installed and configured
- [ ] Python 3.8+ installed
- [ ] Terraform 1.0+ installed
- [ ] Git installed

## Step-by-Step Setup

### 1. Clone Repository (2 minutes)

```bash
git clone https://github.com/iotda-ol/centralized-metadata-management-using-aws-glue-data-catalog-emr-athena.git
cd centralized-metadata-management-using-aws-glue-data-catalog-emr-athena
```

### 2. Configure AWS Credentials (3 minutes)

```bash
# Configure AWS CLI
aws configure

# Verify access
aws sts get-caller-identity
```

### 3. Set Up Python Environment (5 minutes)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
cd python
pip install -e .
cd ..
```

### 4. Create S3 Backend for Terraform (3 minutes)

```bash
# Create unique bucket name
export TF_STATE_BUCKET="tf-state-metadata-mgmt-$(date +%s)"
export AWS_REGION="us-east-1"

# Create S3 bucket
aws s3 mb s3://${TF_STATE_BUCKET} --region ${AWS_REGION}

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ${TF_STATE_BUCKET} \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ${AWS_REGION}
```

### 5. Configure Terraform Backend (2 minutes)

```bash
cd terraform/environments/dev

# Create backend configuration file
cat > backend.conf <<EOF
bucket         = "${TF_STATE_BUCKET}"
key            = "dev/terraform.tfstate"
region         = "${AWS_REGION}"
dynamodb_table = "terraform-state-lock"
encrypt        = true
EOF
```

### 6. Deploy Infrastructure (10-15 minutes)

```bash
# Initialize Terraform
terraform init -backend-config=backend.conf

# Review planned changes
terraform plan

# Apply infrastructure (this will take ~10-15 minutes)
terraform apply
```

**Note**: Type `yes` when prompted to confirm deployment.

### 7. Verify Deployment (2 minutes)

```bash
# Get infrastructure outputs
terraform output

# Verify Glue databases
aws glue get-databases

# Verify S3 buckets
aws s3 ls | grep metadata-mgmt

# Verify Athena workgroups
aws athena list-work-groups
```

### 8. Test the Solution (5 minutes)

```bash
# Return to project root
cd ../../..

# Run example pipeline
python examples/complete_pipeline.py
```

## Quick Test Queries

### Using Python

```python
from metadata_mgmt import CatalogManager, QueryRunner

# List databases
catalog = CatalogManager()
databases = catalog.list_databases()
print(f"Databases: {databases}")

# Query with Athena (if you have data)
runner = QueryRunner(workgroup='primary')
# results = runner.execute_query('SELECT * FROM raw_data.events LIMIT 10')
```

### Using AWS CLI

```bash
# List Glue databases
aws glue get-databases

# Get specific database
aws glue get-database --name metadata-mgmt-dev-raw_data

# List tables in database
aws glue get-tables --database-name metadata-mgmt-dev-raw_data
```

## Next Steps

Now that you have the basic infrastructure running:

1. **Upload sample data** to S3
   ```bash
   aws s3 cp my-data.parquet s3://BUCKET-NAME/raw/events/
   ```

2. **Run a crawler** to discover schema
   ```python
   from metadata_mgmt.glue import CrawlerManager
   
   crawler_mgr = CrawlerManager()
   crawler_mgr.create_crawler(
       name='my-first-crawler',
       role='ARN-FROM-TERRAFORM-OUTPUT',
       database='metadata-mgmt-dev-raw_data',
       s3_targets=['s3://BUCKET-NAME/raw/events/']
   )
   crawler_mgr.start_crawler('my-first-crawler')
   ```

3. **Query your data** with Athena
   ```python
   from metadata_mgmt import QueryRunner
   
   runner = QueryRunner()
   results = runner.execute_query(
       'SELECT * FROM metadata_mgmt_dev_raw_data.events LIMIT 10'
   )
   print(results)
   ```

4. **Explore the documentation**
   - Read [INSTRUCTIONS.md](INSTRUCTIONS.md) for comprehensive 100-step guide
   - Review [Best Practices](docs/guides/best-practices.md)
   - Check [FAQ](docs/guides/faq.md) for common questions

## Troubleshooting

### Issue: Terraform apply fails

**Solution**:
- Check AWS credentials: `aws sts get-caller-identity`
- Verify region is correct
- Check IAM permissions
- Review error messages in terminal

### Issue: Python import errors

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall package
cd python
pip install -e .
```

### Issue: Can't access AWS services

**Solution**:
- Verify AWS CLI configuration: `aws configure list`
- Check IAM user permissions
- Ensure correct region is set

## Clean Up

When you're done testing, clean up resources to avoid charges:

```bash
cd terraform/environments/dev

# Destroy all infrastructure
terraform destroy

# Clean up S3 backend (optional)
aws s3 rb s3://${TF_STATE_BUCKET} --force
aws dynamodb delete-table --table-name terraform-state-lock
```

## Getting Help

- **Documentation**: See [docs/](docs/) folder
- **Examples**: Check [examples/](examples/) folder
- **Issues**: Report bugs on GitHub Issues
- **Questions**: Review [FAQ](docs/guides/faq.md)

## Estimated Costs

For development/testing (assuming minimal usage):
- **AWS Glue**: ~$1-5/month
- **S3 Storage**: ~$1-3/month
- **Athena**: Pay per query (~$5/TB scanned)
- **EMR**: Only when running clusters (terminate when not in use)

**Total estimated**: $5-10/month for light development use

## Summary

You now have:
- ✅ Complete infrastructure deployed
- ✅ Glue Data Catalog configured
- ✅ Athena workgroups set up
- ✅ S3 buckets created
- ✅ Python package installed
- ✅ Ready to process and query data!

**Next**: Upload your data and start building data pipelines!

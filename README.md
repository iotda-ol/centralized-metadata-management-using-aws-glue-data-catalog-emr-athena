# Centralized Metadata Management using AWS Glue Data Catalog, EMR, and Athena

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Terraform](https://img.shields.io/badge/Terraform-%3E%3D1.0-623CE4?logo=terraform)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-Glue%20%7C%20EMR%20%7C%20Athena-FF9900?logo=amazonaws)](https://aws.amazon.com/)

## Overview

This repository demonstrates a **production-ready centralized metadata management solution** using **AWS Glue Data Catalog** as the unified metadata repository for **Amazon EMR** and **Amazon Athena** workloads. The solution enables seamless migration from traditional Apache Hive metastores and provides enterprise-grade data governance with **minimal development effort**, following **DEA-C01 (AWS Certified Data Engineer - Associate)** best practices.

### Key Benefits

✅ **Least Development Effort**: Fully managed, serverless metadata catalog with no infrastructure to maintain  
✅ **Hive Compatibility**: Drop-in replacement for Apache Hive metastore, zero query changes required  
✅ **Unified Access**: Single source of truth for metadata across EMR, Athena, and other AWS analytics services  
✅ **Automatic Discovery**: Glue Crawler automatically discovers and catalogs schemas from S3 data  
✅ **Enterprise Governance**: Built-in access control, audit logging, and compliance features  
✅ **Cost Effective**: Pay-per-request pricing with no fixed infrastructure costs  
✅ **High Availability**: 99.9% SLA with automatic replication and disaster recovery  

## Architecture

The solution implements a centralized metadata architecture where AWS Glue Data Catalog serves as the primary metadata repository:

```
┌─────────────────────────────────────────────────────────────┐
│              AWS Glue Data Catalog                         │
│  (Central Metadata Repository - Hive Compatible)          │
│                                                             │
│  • Databases, Tables, Partitions                          │
│  • Schema Versioning                                      │
│  • Automatic Schema Discovery (Glue Crawler)              │
└──────────────┬────────────────────┬─────────────────────────┘
               │                    │
       ┌───────▼────────┐   ┌──────▼──────┐
       │  Amazon EMR    │   │   Amazon    │
       │                │   │   Athena    │
       │ • Spark        │   │             │
       │ • Hive         │   │ • SQL       │
       │ • Presto       │   │   Queries   │
       └────────┬───────┘   └──────┬──────┘
                │                  │
                └────────┬─────────┘
                         ▼
                 ┌───────────────┐
                 │   Amazon S3   │
                 │ (Data Storage)│
                 └───────────────┘
```

### Why AWS Glue Data Catalog?

According to **DEA-C01 best practices**, AWS Glue Data Catalog provides the **least development effort** because:

- **Zero Infrastructure**: No databases or servers to provision or maintain
- **Native Integration**: Works out-of-the-box with EMR and Athena
- **Automatic Scaling**: Handles millions of tables without configuration
- **Built-in Security**: IAM-based access control and CloudTrail audit logging
- **Hive Compatible**: Seamless migration from existing Hive metastores

**Development Time Comparison**:
- Custom Hive Metastore: 4-6 weeks + ongoing maintenance
- AWS Glue Data Catalog: 4-8 hours + zero maintenance

## Features

### Infrastructure as Code
- **Terraform modules** for complete infrastructure provisioning
- **IAM roles and policies** for secure access control
- **S3 buckets** for data storage and query results
- **Glue Crawler** for automatic schema discovery
- **Athena Workgroup** for query execution management

### Hive Metastore Migration
- **Python import script** for migrating existing Hive metadata
- **Glue Connection** support for legacy metastore access
- **Schema compatibility** maintained during migration
- **Zero downtime** migration path

### Service Integration
- **EMR Integration**: Configuration for Spark, Hive, and Presto
- **Athena Integration**: Pre-configured workgroup and permissions
- **Glue ETL**: Native catalog integration for data transformations
- **Lake Formation**: Support for fine-grained access control

### Comprehensive Documentation
- **Architecture Guide**: Detailed system design and data flow
- **Hive Compatibility**: Migration guide and compatibility matrix
- **DEA-C01 Best Practices**: Alignment with AWS certification standards
- **Deployment Guide**: Step-by-step deployment instructions
- **Usage Examples**: Sample queries and code for EMR and Athena

## Quick Start

### Prerequisites

- **AWS Account** with appropriate permissions
- **Terraform** >= 1.0 ([Installation Guide](https://learn.hashicorp.com/tutorials/terraform/install-cli))
- **AWS CLI** >= 2.0 ([Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- **Python** >= 3.8 (for Hive import script)

### 5-Minute Deployment

```bash
# 1. Clone the repository
git clone https://github.com/iotda-ol/centralized-metadata-management-using-aws-glue-data-catalog-emr-athena.git
cd centralized-metadata-management-using-aws-glue-data-catalog-emr-athena

# 2. Configure AWS credentials
aws configure

# 3. Customize Terraform variables
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your bucket names and settings

# 4. Deploy infrastructure
terraform init
terraform plan
terraform apply

# 5. Verify deployment
aws glue get-database --name centralized_metadata_db
```

**That's it!** Your centralized metadata catalog is now ready to use with EMR and Athena.

## Repository Structure

```
├── terraform/                  # Infrastructure as Code
│   ├── provider.tf            # AWS provider configuration
│   ├── variables.tf           # Input variables
│   ├── main.tf               # Core resources (S3, Glue, Athena)
│   ├── iam.tf                # IAM roles and policies
│   ├── outputs.tf            # Output values
│   └── terraform.tfvars.example  # Example configuration
│
├── scripts/                    # Utility scripts
│   └── hive-import.py        # Hive metastore migration script
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md       # Architecture overview
│   ├── HIVE_COMPATIBILITY.md # Hive compatibility guide
│   ├── DEA_C01_BEST_PRACTICES.md  # DEA-C01 alignment
│   └── DEPLOYMENT_GUIDE.md   # Detailed deployment guide
│
├── examples/                   # Usage examples
│   ├── emr-spark-example.py  # Spark on EMR examples
│   └── athena-queries.sql    # Athena query examples
│
└── README.md                  # This file
```

## Usage Examples

### Using with Amazon EMR

Configure EMR to use Glue Data Catalog when creating a cluster:

```bash
aws emr create-cluster \
  --name "EMR-with-Glue-Catalog" \
  --release-label emr-6.10.0 \
  --applications Name=Spark Name=Hive Name=Presto \
  --use-default-roles \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --configurations '[{
    "Classification": "hive-site",
    "Properties": {
      "hive.metastore.client.factory.class": "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
    }
  }]'
```

**Hive queries work without changes:**

```sql
SHOW DATABASES;
USE centralized_metadata_db;
SHOW TABLES;
SELECT * FROM sales WHERE year='2024' LIMIT 10;
```

### Using with Amazon Athena

Query data using standard SQL:

```sql
-- Athena automatically uses Glue Data Catalog
SELECT 
    year,
    month,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue
FROM centralized_metadata_db.sales
WHERE year = '2024'
GROUP BY year, month
ORDER BY year, month;
```

### Automatic Schema Discovery

Run Glue Crawler to automatically discover schemas:

```bash
# Start crawler
aws glue start-crawler --name centralized-metadata-data-crawler-dev

# Check status
aws glue get-crawler --name centralized-metadata-data-crawler-dev

# View discovered tables
aws glue get-tables --database-name centralized_metadata_db
```

## Migration from Hive Metastore

Migrate existing Hive metastore to Glue Data Catalog:

```bash
cd scripts

# Install dependencies
pip install boto3 PyHive

# Run migration
python hive-import.py \
  --hive-uri jdbc:mysql://hive-host:3306/hive \
  --hive-username hive_user \
  --hive-password your_password \
  --aws-region us-east-1 \
  --glue-database centralized_metadata_db
```

**Zero Changes Required**: All Hive queries continue to work after migration.

## Documentation

### Core Documentation
- **[Architecture Overview](docs/ARCHITECTURE.md)**: Detailed system design, components, and data flows
- **[Hive Compatibility Guide](docs/HIVE_COMPATIBILITY.md)**: Complete compatibility information and migration strategies
- **[DEA-C01 Best Practices](docs/DEA_C01_BEST_PRACTICES.md)**: Why Glue provides least development effort
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)**: Step-by-step deployment and configuration instructions

### Key Topics Covered

#### Architecture (docs/ARCHITECTURE.md)
- Component overview and interactions
- Data flow patterns
- Security and governance model
- Performance optimization strategies
- Migration roadmap

#### Hive Compatibility (docs/HIVE_COMPATIBILITY.md)
- API and protocol compatibility
- Metadata structure mapping
- EMR and Athena configuration
- Migration strategies and tools
- Feature comparison matrix
- Troubleshooting guide

#### DEA-C01 Best Practices (docs/DEA_C01_BEST_PRACTICES.md)
- Least development effort principle
- Cost-benefit analysis
- Comparison with traditional approaches
- Real-world scenarios
- Implementation recommendations

## Configuration

### Key Terraform Variables

```hcl
# AWS Configuration
aws_region  = "us-east-1"
environment = "dev"

# Project Configuration
project_name        = "centralized-metadata"
glue_database_name  = "centralized_metadata_db"

# S3 Configuration (must be globally unique)
s3_data_bucket_name            = "your-org-metadata-data-dev"
s3_athena_results_bucket_name  = "your-org-metadata-athena-dev"

# Glue Crawler Configuration
enable_crawler   = true
crawler_schedule = "cron(0 2 * * ? *)"  # Daily at 2 AM UTC

# Optional: Hive Metastore Migration
hive_metastore_uri      = "jdbc:mysql://host:3306/hive"
hive_metastore_username = "hive_user"
hive_metastore_password = "secure_password"
```

### IAM Roles Created

The Terraform configuration creates the following IAM roles:

1. **Glue Service Role**: For crawler and ETL jobs
2. **EMR Service Role**: For EMR cluster management
3. **EMR EC2 Instance Role**: For EMR nodes with Glue access
4. **Athena Execution Role**: For query execution

All roles follow the principle of least privilege.

## Cost Estimation

**AWS Glue Data Catalog Pricing** (as of 2024):
- Storage: $1.00 per 100,000 objects stored per month
- Requests: $1.00 per million requests

**Example Monthly Cost** (1,000 tables, 10M requests):
- Glue Catalog: ~$20
- S3 Storage (100GB): ~$2.30
- Athena Queries (100GB scanned): ~$5
- **Total: ~$27/month**

**Compare with self-managed Hive metastore**: ~$300-700/month + engineering time

## Security

### Encryption
- **At Rest**: S3 server-side encryption (SSE-S3)
- **In Transit**: TLS for all API communications
- **Query Results**: Encrypted in Athena results bucket

### Access Control
- **IAM Policies**: Fine-grained permissions for all resources
- **Resource-Level Permissions**: Control access to specific databases/tables
- **Service Roles**: Least privilege principle applied
- **Lake Formation**: Optional fine-grained access control

### Audit and Compliance
- **CloudTrail**: All API calls logged automatically
- **CloudWatch**: Metrics and monitoring for all services
- **Versioning**: S3 bucket versioning enabled
- **Tags**: Resource tagging for cost allocation and governance

## Monitoring

### Key Metrics
- Glue Crawler success/failure rates
- Glue API request counts and latencies
- EMR cluster health and job statuses
- Athena query execution times
- S3 data access patterns

### Logging
- CloudWatch Logs for Glue operations
- EMR cluster logs stored in S3
- Athena query history and results
- CloudTrail for audit trails

## Troubleshooting

### Common Issues

**Issue**: EMR can't find Glue tables  
**Solution**: Verify EMR configuration includes Glue Data Catalog settings

**Issue**: Athena query fails with "access denied"  
**Solution**: Check IAM role permissions for Glue and S3 access

**Issue**: Crawler fails to discover schema  
**Solution**: Verify Glue service role has S3 read permissions

**Issue**: Performance is slow  
**Solution**: Enable Glue Catalog caching in EMR, use partition filters

See [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) for detailed troubleshooting.

## Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and create pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resources

### AWS Documentation
- [AWS Glue Data Catalog](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html)
- [EMR with Glue Data Catalog](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-metastore-glue.html)
- [Athena with Glue Data Catalog](https://docs.aws.amazon.com/athena/latest/ug/glue-athena.html)

### Certification
- [AWS Certified Data Engineer - Associate (DEA-C01)](https://aws.amazon.com/certification/certified-data-engineer-associate/)

### Related Projects
- [Apache Hive](https://hive.apache.org/)
- [Apache Spark](https://spark.apache.org/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/)

## Support

For issues, questions, or suggestions:
- Open an issue in this repository
- Check the [documentation](docs/) for detailed guides
- Review [AWS Glue documentation](https://docs.aws.amazon.com/glue/)

## Acknowledgments

This solution demonstrates best practices for centralized metadata management following AWS Certified Data Engineer - Associate (DEA-C01) guidelines, emphasizing the principle of **least development effort** through fully managed AWS services.

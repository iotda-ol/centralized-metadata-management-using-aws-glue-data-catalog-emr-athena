# Centralized Metadata Management using AWS Glue Data Catalog, EMR, and Athena

A comprehensive, production-ready solution for centralized metadata management using AWS Glue Data Catalog. This repository provides infrastructure as code (Terraform), modular Python libraries, and extensive documentation to build a robust data lake metadata management system.

## Overview

This repository demonstrates a centralized metadata management solution using AWS Glue Data Catalog. Existing Apache Hive metadata is imported to provide a shared schema repository accessible by Amazon EMR and Amazon Athena. The solution minimizes development effort and follows DEA-C01 data governance best practices.

## Features

- **Modular Terraform Infrastructure**: Reusable modules for Glue, EMR, Athena, S3, IAM, and VPC
- **Python Libraries**: Well-structured, tested Python code for catalog management, query execution, and job submission
- **Comprehensive Documentation**: 100-step instruction manual from novice to expert
- **Production-Ready**: Includes monitoring, security, encryption, and disaster recovery
- **Best Practices**: Follows AWS Well-Architected Framework and DEA-C01 standards

## Repository Structure

```
.
├── terraform/              # Infrastructure as Code
│   ├── modules/           # Reusable Terraform modules
│   │   ├── glue/         # AWS Glue Data Catalog
│   │   ├── emr/          # Amazon EMR clusters
│   │   ├── athena/       # Amazon Athena workgroups
│   │   ├── s3/           # S3 buckets (data lake, scripts, logs)
│   │   ├── iam/          # IAM roles and policies
│   │   ├── vpc/          # VPC and networking
│   │   └── monitoring/   # CloudWatch monitoring
│   └── environments/     # Environment-specific configs
│       ├── dev/
│       ├── staging/
│       └── prod/
├── python/                # Python codebase
│   ├── src/
│   │   └── metadata_mgmt/
│   │       ├── glue/     # Glue catalog operations
│   │       ├── emr/      # EMR job management
│   │       ├── athena/   # Athena query execution
│   │       ├── utils/    # Common utilities
│   │       └── monitoring/ # Monitoring and metrics
│   └── tests/            # Unit and integration tests
├── docs/                 # Documentation
│   ├── guides/          # User guides
│   └── architecture/    # Architecture documentation
├── scripts/             # Utility scripts
├── examples/            # Example configurations
│   ├── data/           # Sample data
│   ├── configs/        # Example configs
│   └── workflows/      # Example workflows
└── INSTRUCTIONS.md      # Comprehensive 100-step manual

```

## Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- Python 3.8 or higher
- Terraform 1.0 or higher
- AWS CLI v2
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/iotda-ol/centralized-metadata-management-using-aws-glue-data-catalog-emr-athena.git
   cd centralized-metadata-management-using-aws-glue-data-catalog-emr-athena
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cd python && pip install -e .
   ```

3. **Configure AWS credentials**:
   ```bash
   aws configure
   ```

4. **Initialize Terraform**:
   ```bash
   cd terraform/environments/dev
   terraform init
   ```

## Usage

### Deploy Infrastructure

```bash
cd terraform/environments/dev
terraform plan
terraform apply
```

### Use Python Libraries

```python
from metadata_mgmt import CatalogManager, QueryRunner, JobSubmitter

# Create database
catalog = CatalogManager()
catalog.create_database('my_database', 'My data lake database')

# Create table
schema = [
    {'Name': 'id', 'Type': 'bigint'},
    {'Name': 'name', 'Type': 'string'}
]
catalog.create_table(
    database='my_database',
    table='users',
    schema=schema,
    location='s3://my-bucket/data/users/',
    format='parquet'
)

# Query with Athena
runner = QueryRunner(workgroup='primary')
results = runner.execute_query(
    'SELECT * FROM my_database.users LIMIT 10'
)
print(results)

# Submit EMR job
submitter = JobSubmitter(cluster_id='j-XXXXXXXXXXXXX')
step_id = submitter.submit_spark_job(
    script='s3://my-bucket/scripts/process_data.py',
    args=['--input', 's3://my-bucket/raw/']
)
```

## Documentation

- **[INSTRUCTIONS.md](INSTRUCTIONS.md)**: Comprehensive 100-step manual (novice to expert)
- **[Architecture Guide](docs/architecture/)**: System architecture and design
- **[User Guides](docs/guides/)**: Best practices, troubleshooting, and FAQs

## Architecture

The solution consists of:

1. **AWS Glue Data Catalog**: Central metadata repository
2. **Amazon EMR**: Big data processing with Hive/Spark
3. **Amazon Athena**: Serverless SQL queries
4. **Amazon S3**: Data lake storage (raw, processed, curated)
5. **AWS IAM**: Security and access control
6. **CloudWatch**: Monitoring and logging

All components are integrated through the Glue Data Catalog, providing a unified metadata layer.

## Testing

```bash
cd python/

# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/ --cov=src/ --cov-report=html
```

## Security

- All S3 buckets have encryption enabled
- IAM roles follow least privilege principle
- VPC isolation for EMR clusters
- CloudTrail enabled for audit logging
- Secrets managed via AWS Secrets Manager

## Cost Optimization

- Partition data for efficient queries
- Use columnar formats (Parquet/ORC)
- Implement data lifecycle policies
- Right-size EMR instances
- Monitor Athena data scanned

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support:
- Open an issue in this repository
- Review the [troubleshooting guide](docs/guides/troubleshooting.md)
- Check the [FAQ](docs/guides/faq.md)

## Acknowledgments

- AWS Glue documentation
- Amazon EMR best practices
- Amazon Athena user guide
- DEA-C01 certification guide
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

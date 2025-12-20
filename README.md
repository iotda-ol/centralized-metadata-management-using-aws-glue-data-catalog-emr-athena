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

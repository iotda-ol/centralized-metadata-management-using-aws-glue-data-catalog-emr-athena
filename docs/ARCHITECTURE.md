# Architecture Overview

## Centralized Metadata Management with AWS Glue Data Catalog

This solution implements a centralized metadata management system using AWS Glue Data Catalog as the primary metadata repository, providing unified schema management for Amazon EMR and Amazon Athena workloads.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Existing Hive Metastore                      │
│                     (Optional Migration)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Import/Migration
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AWS Glue Data Catalog                          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Database   │  │    Tables    │  │  Partitions  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐         │
│  │           Glue Crawler                            │         │
│  │  (Automatic Schema Discovery & Updates)          │         │
│  └──────────────────────────────────────────────────┘         │
└────────────┬──────────────────────┬──────────────────────────┘
             │                      │
             │                      │
    ┌────────▼────────┐    ┌───────▼────────┐
    │  Amazon EMR     │    │ Amazon Athena  │
    │                 │    │                │
    │ • Spark Jobs    │    │ • SQL Queries  │
    │ • Hive Queries  │    │ • Analysis     │
    │ • Presto        │    │                │
    └────────┬────────┘    └───────┬────────┘
             │                     │
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   Amazon S3      │
              │  (Data Storage)  │
              └──────────────────┘
```

## Components

### 1. AWS Glue Data Catalog
**Purpose**: Central metadata repository

**Key Features**:
- Hive Metastore compatible
- Serverless and fully managed
- Automatic schema versioning
- Integration with AWS analytics services
- Fine-grained access control via IAM

**Benefits**:
- No infrastructure to manage
- High availability and durability
- Consistent metadata across services
- Cost-effective (pay-per-request pricing)

### 2. AWS Glue Crawler
**Purpose**: Automatic schema discovery and updates

**Features**:
- Automatically scans S3 data sources
- Infers schema from data files
- Detects new partitions
- Updates table definitions
- Scheduled execution

**Configuration**:
- Schedule: Configurable (default: daily at 2 AM UTC)
- Schema change policy: Update in database
- Partition handling: Inherit from table

### 3. Amazon EMR Integration
**Purpose**: Big data processing using centralized metadata

**Hive Compatibility**:
- EMR uses Glue Data Catalog as Hive metastore
- Configuration via `hive.metastore.client.factory.class`
- Backward compatible with existing Hive queries
- Supports Spark, Hive, and Presto workloads

**Key Configuration**:
```json
{
  "classification": "hive-site",
  "properties": {
    "hive.metastore.client.factory.class": "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
  }
}
```

### 4. Amazon Athena Integration
**Purpose**: Interactive SQL analytics on S3 data

**Features**:
- Native integration with Glue Data Catalog
- No configuration required (default metastore)
- Serverless query execution
- Standard SQL support
- JDBC/ODBC connectivity

### 5. IAM Roles and Permissions
**Purpose**: Secure access control

**Roles Created**:
1. **Glue Service Role**: For crawler and ETL jobs
   - Access to S3 data sources
   - Glue Data Catalog permissions
   - CloudWatch logging

2. **EMR Service Role**: For cluster management
   - EC2, S3, and Glue permissions
   - Cluster lifecycle management

3. **EMR EC2 Instance Role**: For EMR nodes
   - Read/write S3 data
   - Full Glue Data Catalog access
   - Table and partition management

4. **Athena Execution Role**: For query execution
   - Read Glue Data Catalog
   - Read S3 data sources
   - Write query results to S3

## Data Flow

### 1. Schema Discovery Flow
```
S3 Data → Glue Crawler → Schema Inference → Glue Catalog → Available to EMR/Athena
```

### 2. EMR Query Flow
```
EMR Job → Request Metadata → Glue Catalog → Return Schema → Read S3 Data → Process
```

### 3. Athena Query Flow
```
SQL Query → Glue Catalog Lookup → Generate Execution Plan → Read S3 → Return Results
```

### 4. Hive Migration Flow
```
Hive Metastore → Extract Metadata → Transform to Glue Format → Import to Glue Catalog
```

## Key Benefits

### 1. Least Development Effort (DEA-C01 Best Practice)
- **No Custom Code**: Uses AWS managed services
- **No Infrastructure**: Serverless architecture
- **No Maintenance**: AWS handles updates and scaling
- **Quick Deployment**: Terraform automation
- **Standard APIs**: Compatible with existing tools

### 2. Hive Compatibility
- **Drop-in Replacement**: EMR automatically uses Glue as Hive metastore
- **No Query Changes**: Existing Hive queries work unchanged
- **Metadata Compatibility**: Full support for Hive table formats
- **Partition Support**: Native Hive partition handling

### 3. Centralized Governance
- **Single Source of Truth**: One metadata repository
- **Consistent Schemas**: Same definitions across services
- **Access Control**: IAM-based permissions
- **Audit Trail**: CloudTrail logging for all operations
- **Data Lineage**: Track metadata changes over time

### 4. Cost Optimization
- **Pay-per-Request**: No fixed costs for metadata storage
- **No Redundancy**: Eliminate duplicate metastores
- **Serverless**: No idle infrastructure costs
- **Efficient Crawling**: Scheduled schema discovery

### 5. Scalability
- **Unlimited Tables**: No practical limits
- **High Throughput**: Handles millions of metadata requests
- **Multi-Region**: Deploy across AWS regions
- **Cross-Account**: Share catalogs across AWS accounts

## Security Considerations

### 1. Encryption
- **At Rest**: S3 server-side encryption (SSE-S3)
- **In Transit**: TLS for all API calls
- **Query Results**: Encrypted in Athena results bucket

### 2. Access Control
- **IAM Policies**: Fine-grained permissions
- **Resource-Level**: Control access to specific databases/tables
- **Service Roles**: Least privilege principle
- **Cross-Account**: AWS Lake Formation for advanced governance

### 3. Audit and Compliance
- **CloudTrail**: All API calls logged
- **CloudWatch**: Metrics and alarms
- **Versioning**: S3 bucket versioning enabled
- **Tags**: Resource tagging for cost allocation

## Migration Strategy

### Phase 1: Assessment
1. Inventory existing Hive metastore tables
2. Identify dependencies and access patterns
3. Plan migration schedule
4. Set up Glue Data Catalog infrastructure

### Phase 2: Infrastructure Setup
1. Deploy Terraform configuration
2. Create IAM roles and policies
3. Set up S3 buckets
4. Configure Glue Crawler

### Phase 3: Metadata Migration
1. Extract metadata from Hive metastore
2. Transform to Glue-compatible format
3. Import using migration script
4. Verify table definitions

### Phase 4: Service Integration
1. Configure EMR to use Glue Data Catalog
2. Set up Athena workgroups
3. Update application configurations
4. Test queries and jobs

### Phase 5: Cutover
1. Run parallel testing period
2. Validate results match Hive metastore
3. Switch production workloads
4. Decommission old metastore

## Best Practices

### 1. Naming Conventions
- Use lowercase for database and table names
- Avoid special characters
- Use underscores instead of hyphens
- Keep names descriptive but concise

### 2. Partitioning Strategy
- Partition large tables by date/time
- Avoid over-partitioning (keep partitions > 1GB)
- Use Glue Crawler for partition discovery
- Regularly add new partitions

### 3. Schema Evolution
- Use Glue Crawler for automatic schema updates
- Version control table definitions
- Test schema changes in non-production first
- Document breaking changes

### 4. Performance Optimization
- Use columnar formats (Parquet, ORC)
- Enable compression
- Partition appropriately
- Use Glue Catalog caching in EMR

### 5. Cost Management
- Schedule crawlers during off-peak hours
- Use lifecycle policies for old query results
- Monitor Glue API usage
- Implement tagging strategy

## Monitoring and Operations

### Key Metrics to Monitor
- Glue Crawler success/failure rate
- Glue API request count and latency
- EMR cluster metadata access patterns
- Athena query execution times
- S3 data access patterns

### Alerting
- Crawler failures
- API throttling errors
- Unusual access patterns
- Cost anomalies

### Maintenance Tasks
- Review and update IAM policies
- Clean up old Athena query results
- Archive or delete obsolete tables
- Update Terraform configurations
- Review CloudWatch logs

## Troubleshooting

### Common Issues

**Issue**: EMR not finding tables
- **Solution**: Verify EMR configuration for Glue Data Catalog
- Check IAM role permissions
- Ensure table locations are accessible

**Issue**: Schema mismatches
- **Solution**: Re-run Glue Crawler
- Manually update table schema
- Check data file formats

**Issue**: Slow query performance
- **Solution**: Review partition strategy
- Convert to columnar format
- Optimize file sizes
- Enable Glue Catalog caching

**Issue**: Access denied errors
- **Solution**: Review IAM policies
- Check resource-based policies
- Verify role trust relationships
- Check S3 bucket policies

## References

- [AWS Glue Data Catalog](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html)
- [EMR with Glue Data Catalog](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-metastore-glue.html)
- [Athena with Glue Data Catalog](https://docs.aws.amazon.com/athena/latest/ug/glue-athena.html)
- [DEA-C01 Exam Guide](https://aws.amazon.com/certification/certified-data-engineer-associate/)

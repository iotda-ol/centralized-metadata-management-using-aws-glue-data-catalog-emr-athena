# Hive Compatibility Guide

## Overview

AWS Glue Data Catalog is fully compatible with Apache Hive metastore, making it a seamless replacement for traditional Hive metastore implementations. This guide explains the compatibility features, migration considerations, and best practices.

## Why AWS Glue Data Catalog is Hive-Compatible

### 1. Protocol Compatibility
- **API Compatibility**: Glue Data Catalog implements the Hive metastore API
- **Thrift Protocol**: Supports Hive metastore Thrift protocol
- **Client Libraries**: Works with standard Hive metastore client libraries
- **Version Support**: Compatible with Hive 2.x and 3.x

### 2. Metadata Structure Compatibility

#### Databases
Hive databases map directly to Glue databases:
- Same naming conventions
- Same properties and parameters
- Location URIs preserved

#### Tables
Hive tables are fully supported:
- External tables
- Managed tables
- Views
- Table properties and parameters
- SerDe (Serialization/Deserialization) configurations

#### Partitions
Full partition support:
- Static partitions
- Dynamic partitions
- Partition pruning
- Partition metadata
- Custom partition locations

#### Storage Formats
All common Hive storage formats:
- Text (CSV, TSV)
- JSON
- Parquet
- ORC
- Avro
- SequenceFile
- RCFile

#### SerDe Support
Standard and custom SerDes:
- LazySimpleSerDe
- ParquetSerDe
- OrcSerDe
- JsonSerDe
- OpenCSVSerDe
- Custom SerDe libraries

## Using Glue Data Catalog with EMR

### Configuration

EMR automatically uses Glue Data Catalog when you enable it during cluster creation.

#### Option 1: EMR Console
Enable "Use for Hive table metadata" when creating a cluster.

#### Option 2: AWS CLI
```bash
aws emr create-cluster \
  --name "EMR-with-Glue-Catalog" \
  --release-label emr-6.10.0 \
  --applications Name=Spark Name=Hive Name=Presto \
  --ec2-attributes KeyName=myKey,InstanceProfile=EMR_EC2_DefaultRole \
  --service-role EMR_DefaultRole \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --use-default-roles \
  --configurations '[
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
  ]'
```

#### Option 3: Terraform
```hcl
resource "aws_emr_cluster" "cluster" {
  name          = "emr-glue-catalog"
  release_label = "emr-6.10.0"
  applications  = ["Spark", "Hive", "Presto"]

  configurations_json = jsonencode([
    {
      Classification = "hive-site"
      Properties = {
        "hive.metastore.client.factory.class" = "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
      }
    },
    {
      Classification = "spark-hive-site"
      Properties = {
        "hive.metastore.client.factory.class" = "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
      }
    }
  ])
  
  # ... other configuration
}
```

### Hive Query Compatibility

All standard Hive DDL and DML operations work without modification:

#### CREATE DATABASE
```sql
CREATE DATABASE IF NOT EXISTS my_database
COMMENT 'My database description'
LOCATION 's3://my-bucket/database/';
```

#### CREATE TABLE
```sql
CREATE EXTERNAL TABLE IF NOT EXISTS my_table (
  id BIGINT,
  name STRING,
  timestamp TIMESTAMP
)
PARTITIONED BY (year STRING, month STRING)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://my-bucket/data/my_table/';
```

#### ALTER TABLE
```sql
ALTER TABLE my_table ADD COLUMNS (new_column STRING);
ALTER TABLE my_table SET LOCATION 's3://new-bucket/data/';
```

#### ADD PARTITION
```sql
ALTER TABLE my_table ADD PARTITION (year='2024', month='01')
LOCATION 's3://my-bucket/data/my_table/year=2024/month=01/';
```

#### DROP TABLE
```sql
DROP TABLE IF EXISTS my_table;
```

#### SHOW DATABASES/TABLES
```sql
SHOW DATABASES;
SHOW TABLES IN my_database;
DESCRIBE FORMATTED my_table;
```

### Spark SQL with Glue Catalog

Spark SQL automatically uses Glue Data Catalog when configured:

```python
from pyspark.sql import SparkSession

# Create Spark session (Glue Catalog configured via EMR)
spark = SparkSession.builder \
    .appName("GlueCatalogExample") \
    .getOrCreate()

# Query tables from Glue Catalog
df = spark.sql("SELECT * FROM my_database.my_table WHERE year='2024'")
df.show()

# Create table in Glue Catalog
spark.sql("""
    CREATE TABLE my_database.new_table (
        id INT,
        value STRING
    )
    USING parquet
    LOCATION 's3://my-bucket/new_table/'
""")
```

### Presto with Glue Catalog

Presto automatically integrates with Glue Data Catalog:

```sql
-- Query using Presto
SELECT * FROM hive.my_database.my_table
WHERE year = '2024' AND month = '01';

-- Create table
CREATE TABLE hive.my_database.presto_table (
    id bigint,
    name varchar
)
WITH (
    format = 'PARQUET',
    external_location = 's3://my-bucket/presto_table/'
);
```

## Migration from Hive Metastore to Glue Data Catalog

### Migration Strategies

#### 1. Direct API Migration
Use the provided Python script to migrate metadata:

```bash
python scripts/hive-import.py \
  --hive-metastore-uri "jdbc:mysql://host:3306/hive" \
  --hive-username "hive_user" \
  --hive-password "password" \
  --aws-region "us-east-1" \
  --glue-database "my_database"
```

#### 2. Export/Import Method
Export Hive metastore and import to Glue:

```bash
# Export from Hive
hive -e "SHOW DATABASES;" > databases.txt
hive -e "SHOW TABLES IN database_name;" > tables.txt

# For each table, get metadata
hive -e "SHOW CREATE TABLE database_name.table_name;" > create_table.sql

# Execute in EMR with Glue Catalog enabled
hive -f create_table.sql
```

#### 3. Crawler-Based Discovery
Let Glue Crawler discover schemas from S3:

```bash
# Create crawler
aws glue create-crawler \
  --name my-crawler \
  --role arn:aws:iam::123456789012:role/GlueServiceRole \
  --database-name my_database \
  --targets '{"S3Targets":[{"Path":"s3://my-bucket/data/"}]}'

# Start crawler
aws glue start-crawler --name my-crawler
```

### Migration Checklist

- [ ] Inventory all Hive databases and tables
- [ ] Document custom SerDe libraries (migrate if needed)
- [ ] Test sample tables in Glue Catalog
- [ ] Verify partition metadata
- [ ] Check table properties and parameters
- [ ] Test queries with EMR using Glue Catalog
- [ ] Validate data access permissions
- [ ] Update application configurations
- [ ] Plan cutover window
- [ ] Create rollback plan

### Mapping Considerations

#### Table Types
| Hive | Glue Data Catalog |
|------|-------------------|
| MANAGED_TABLE | MANAGED_TABLE (not recommended, use EXTERNAL) |
| EXTERNAL_TABLE | EXTERNAL_TABLE (recommended) |
| VIRTUAL_VIEW | VIRTUAL_VIEW |

#### Storage Descriptors
All Hive storage descriptor properties are preserved:
- Input/Output formats
- SerDe information
- Column definitions
- Location URIs
- Bucket information
- Compression

#### Custom Properties
All custom table properties are maintained:
- `last_modified_time`
- `numFiles`
- `numRows`
- `totalSize`
- Custom application properties

## Feature Comparison

| Feature | Hive Metastore | Glue Data Catalog | Notes |
|---------|----------------|-------------------|-------|
| Table metadata | ✅ | ✅ | Full compatibility |
| Partition support | ✅ | ✅ | All partition types supported |
| Custom SerDe | ✅ | ✅ | Must be available on EMR |
| Views | ✅ | ✅ | Fully supported |
| Statistics | ✅ | ✅ | Column and table statistics |
| Transactions | ✅ | ⚠️ | Hive ACID not supported in Glue |
| Management overhead | High | None | Glue is fully managed |
| High availability | Manual | Built-in | Glue provides HA automatically |
| Scalability | Limited | Unlimited | Glue scales automatically |
| Cost | Infrastructure | Pay-per-request | Glue is more cost-effective |

### Known Limitations

1. **Hive ACID Transactions**: Not supported in Glue Data Catalog
   - Use Delta Lake or Apache Iceberg for transactional tables
   - Consider Glue for non-transactional tables only

2. **Stored Procedures**: Not supported
   - Migrate to Glue ETL jobs or Step Functions

3. **Indexes**: Not supported
   - Use partitioning and columnar formats instead
   - Leverage Athena's query optimization

4. **Custom UDFs in Metadata**: Not stored in catalog
   - Deploy UDF JARs to EMR clusters separately
   - Use Glue Python shell or PySpark for custom logic

## Performance Considerations

### Metadata Caching

Enable Glue Data Catalog client caching in EMR:

```json
{
  "Classification": "hive-site",
  "Properties": {
    "aws.glue.cache.db.enable": "true",
    "aws.glue.cache.db.size": "1000",
    "aws.glue.cache.db.ttl-mins": "30",
    "aws.glue.cache.table.enable": "true",
    "aws.glue.cache.table.size": "1000",
    "aws.glue.cache.table.ttl-mins": "30"
  }
}
```

### Best Practices

1. **Partition Pruning**: Use partition filters in queries
2. **Columnar Formats**: Convert to Parquet or ORC
3. **File Size Optimization**: Keep files between 128MB-1GB
4. **Statistics**: Run ANALYZE TABLE to update statistics
5. **Compression**: Enable compression for storage efficiency

## Troubleshooting

### Common Issues

#### Issue: Tables not visible after migration
**Symptoms**: Tables exist in Hive but not in Glue Catalog

**Solutions**:
1. Verify table was successfully imported
2. Check database name (case-sensitive)
3. Verify IAM permissions
4. Check EMR configuration

#### Issue: SerDe not found
**Symptoms**: "SerDe class not found" errors

**Solutions**:
1. Install SerDe JAR on EMR cluster
2. Add JAR to Hive classpath
3. Use standard SerDe if possible

#### Issue: Partition metadata incomplete
**Symptoms**: Missing partitions in Glue Catalog

**Solutions**:
1. Run MSCK REPAIR TABLE
2. Use Glue Crawler to discover partitions
3. Manually add partitions using ALTER TABLE

#### Issue: Performance degradation
**Symptoms**: Queries slower than with Hive metastore

**Solutions**:
1. Enable Glue Catalog caching
2. Optimize partition strategy
3. Use columnar file formats
4. Update table statistics

### Verification Commands

```sql
-- Check database in Glue Catalog
SHOW DATABASES;

-- Verify table structure
DESCRIBE FORMATTED database_name.table_name;

-- Check partitions
SHOW PARTITIONS database_name.table_name;

-- Repair partitions
MSCK REPAIR TABLE database_name.table_name;

-- Update statistics
ANALYZE TABLE database_name.table_name COMPUTE STATISTICS;
```

## Resources

- [AWS Glue Data Catalog Overview](https://docs.aws.amazon.com/glue/latest/dg/components-overview.html)
- [Hive Metastore Compatibility](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-hive-metastore-glue.html)
- [EMR with Glue Data Catalog](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-metastore-glue.html)
- [Apache Hive Documentation](https://hive.apache.org/)
- [Migrating from MySQL Metastore](https://aws.amazon.com/blogs/big-data/migrate-your-amazon-emr-hive-metastore-to-aws-glue/)

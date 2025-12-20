# Troubleshooting Guide

## Common Issues and Solutions

### Glue Catalog Issues

#### Issue: Crawler not finding tables
**Symptoms**: Crawler runs successfully but no tables created

**Solutions**:
1. Check S3 bucket permissions - Glue role needs read access
2. Verify data format is supported
3. Check if data files exist in the target path
4. Review crawler logs in CloudWatch

```bash
aws logs tail /aws-glue/crawlers --follow
```

#### Issue: Table schema incorrect
**Symptoms**: Table created but columns wrong or missing

**Solutions**:
1. Delete and re-run crawler
2. Use custom classifier if data format is unusual
3. Manually define table schema

```python
from metadata_mgmt.glue import CatalogManager

catalog = CatalogManager()
catalog.delete_table('database', 'table')
# Re-create with correct schema
```

### EMR Issues

#### Issue: EMR cluster fails to start
**Symptoms**: Cluster stuck in STARTING or fails to WAITING

**Solutions**:
1. Check VPC and subnet configuration
2. Verify security group rules
3. Ensure EC2 instance limits not exceeded
4. Review bootstrap action logs

```bash
aws emr describe-cluster --cluster-id j-XXXXX
aws emr list-bootstrap-actions --cluster-id j-XXXXX
```

#### Issue: Hive cannot access Glue Catalog
**Symptoms**: Hive queries fail with metadata errors

**Solutions**:
1. Verify Glue Data Catalog integration in EMR configuration
2. Check IAM role permissions
3. Ensure hive-site.xml configured correctly

```xml
<property>
  <name>hive.metastore.client.factory.class</name>
  <value>com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory</value>
</property>
```

### Athena Issues

#### Issue: Query fails with "HIVE_CANNOT_OPEN_SPLIT"
**Symptoms**: Athena query fails when reading data

**Solutions**:
1. Check S3 bucket permissions
2. Verify table location is correct
3. Ensure files are not corrupted
4. Check if encryption is consistent

```sql
-- Check table location
SHOW CREATE TABLE database.table;
```

#### Issue: Slow query performance
**Symptoms**: Queries take longer than expected

**Solutions**:
1. Add partitions to table
2. Use columnar format (Parquet/ORC)
3. Compress data files
4. Optimize query to select only needed columns

```sql
-- Add partition
ALTER TABLE database.table 
ADD PARTITION (year='2024', month='01') 
LOCATION 's3://bucket/path/year=2024/month=01/';
```

### Python Library Issues

#### Issue: Import errors
**Symptoms**: Cannot import metadata_mgmt modules

**Solutions**:
1. Ensure package is installed: `pip install -e .`
2. Activate virtual environment
3. Check Python version (3.8+)

```bash
python -c "import metadata_mgmt; print('Success')"
```

#### Issue: Boto3 credential errors
**Symptoms**: NoCredentialsError or InvalidClientTokenId

**Solutions**:
1. Configure AWS CLI: `aws configure`
2. Set environment variables
3. Use IAM role if running on EC2

```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-east-1
```

## Getting Help

1. Check CloudWatch Logs
2. Review AWS Service Health Dashboard
3. Consult AWS documentation
4. Open GitHub issue with logs and error details

# Best Practices Guide

## Data Lake Organization

### S3 Bucket Structure

```
data-lake-bucket/
├── raw/                    # Landing zone for raw data
│   ├── events/
│   │   └── year=2024/
│   │       └── month=01/
│   │           └── day=15/
│   ├── users/
│   └── transactions/
├── processed/              # Cleaned and validated data
│   ├── events/
│   └── users/
└── curated/               # Analytics-ready data
    ├── user_summary/
    ├── daily_metrics/
    └── reports/
```

### File Naming Conventions

- Use lowercase
- Use hyphens for separators
- Include timestamp in filename
- Add version if applicable

Examples:
```
events-2024-01-15-v1.parquet
user-profile-20240115-001.parquet
transaction-batch-2024-01-15-12-30-00.parquet
```

## Partitioning Strategy

### When to Partition

**Partition when:**
- Data volume > 1GB
- Queries filter on specific columns frequently
- Data has natural time-based or categorical divisions

**Don't partition when:**
- Total data size < 100MB
- Partitions would be < 10MB each
- No consistent query pattern

### Partition Key Selection

**Good partition keys:**
- Date (year, month, day)
- Region/Geography
- Product category
- Customer segment

**Avoid:**
- High cardinality (e.g., user_id)
- Timestamp (use date instead)
- Constantly changing values

### Example Partition Structure

```sql
CREATE EXTERNAL TABLE events (
    event_id STRING,
    user_id STRING,
    event_type STRING,
    properties STRING
)
PARTITIONED BY (
    year STRING,
    month STRING,
    day STRING
)
STORED AS PARQUET
LOCATION 's3://bucket/events/';
```

## File Format Selection

### Format Comparison

| Format  | Use Case | Pros | Cons |
|---------|----------|------|------|
| Parquet | Analytics | Best compression, columnar, fast queries | Not human-readable |
| ORC | Analytics | Excellent compression, ACID support | Limited tool support |
| JSON | Logs, semi-structured | Human-readable, flexible schema | Large size, slow queries |
| CSV | Simple data, exports | Universal support, simple | No compression, no types |
| Avro | Streaming, schemas | Schema evolution, compact | Not columnar |

### Recommended: Parquet

```python
# Write Parquet with Spark
df.write \
    .mode('append') \
    .partitionBy('year', 'month', 'day') \
    .parquet('s3://bucket/events/')

# Compression
df.write \
    .option('compression', 'snappy') \
    .parquet('s3://bucket/events/')
```

## Schema Management

### Schema Design Principles

1. **Use appropriate data types**
   ```sql
   -- Good
   user_id BIGINT
   created_at TIMESTAMP
   
   -- Avoid
   user_id STRING
   created_at STRING
   ```

2. **Normalize when needed**
   - Separate dimension and fact tables
   - Avoid deep nesting in JSON

3. **Document schemas**
   ```sql
   CREATE TABLE users (
       user_id BIGINT COMMENT 'Unique user identifier',
       username STRING COMMENT 'User login name',
       created_at TIMESTAMP COMMENT 'Account creation timestamp'
   )
   COMMENT 'User profile information';
   ```

### Schema Evolution

**Backward compatible changes:**
- Adding new columns (at end)
- Adding new partitions

**Breaking changes:**
- Removing columns
- Changing data types
- Renaming columns

**Handle evolution:**
```python
# Add new column with default
ALTER TABLE users ADD COLUMNS (email STRING);

# Create new version
CREATE TABLE users_v2 AS 
SELECT *, NULL as email FROM users_v1;
```

## Query Optimization

### Athena Best Practices

1. **Partition Pruning**
   ```sql
   -- Good: Uses partition filter
   SELECT * FROM events 
   WHERE year='2024' AND month='01' AND day='15';
   
   -- Bad: Scans all partitions
   SELECT * FROM events 
   WHERE timestamp >= '2024-01-15';
   ```

2. **Column Selection**
   ```sql
   -- Good: Select only needed columns
   SELECT user_id, event_type FROM events;
   
   -- Bad: Scans all columns
   SELECT * FROM events;
   ```

3. **Use CTAS for intermediate results**
   ```sql
   -- Create optimized table
   CREATE TABLE events_summary 
   WITH (format='PARQUET', parquet_compression='SNAPPY')
   AS SELECT 
       date, 
       COUNT(*) as event_count
   FROM events 
   GROUP BY date;
   ```

4. **Enable result caching**
   ```sql
   -- Results cached for 60 minutes
   -- Subsequent identical queries are free
   ```

### EMR/Spark Best Practices

1. **Optimize Spark Configuration**
   ```python
   spark = SparkSession.builder \
       .appName("ETL Job") \
       .config("spark.sql.adaptive.enabled", "true") \
       .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
       .config("spark.sql.files.maxPartitionBytes", "134217728") \
       .getOrCreate()
   ```

2. **Use DataFrame API**
   ```python
   # Good: DataFrame API (optimized)
   df.filter(col('year') == '2024') \
     .groupBy('user_id') \
     .count()
   
   # Avoid: RDD operations (not optimized)
   rdd.filter(lambda x: x['year'] == '2024') \
      .map(lambda x: (x['user_id'], 1)) \
      .reduceByKey(lambda a, b: a + b)
   ```

3. **Broadcast small tables**
   ```python
   from pyspark.sql.functions import broadcast
   
   # Broadcast small dimension table
   result = large_fact.join(
       broadcast(small_dim),
       'user_id'
   )
   ```

## Cost Optimization

### S3 Storage Costs

1. **Use compression**
   - Parquet with Snappy: ~70% compression
   - Gzip: Better compression, slower queries

2. **Implement lifecycle policies**
   ```json
   {
     "Rules": [{
       "Filter": {"Prefix": "raw/"},
       "Transitions": [{
         "Days": 90,
         "StorageClass": "GLACIER"
       }],
       "Expiration": {
         "Days": 365
       }
     }]
   }
   ```

3. **Delete unnecessary data**
   - Remove duplicate files
   - Clean up temporary data
   - Archive old data

### Athena Query Costs

1. **Monitor data scanned**
   ```sql
   -- Check in query history
   SELECT query_id, data_scanned_in_bytes/1024/1024/1024 as gb_scanned
   FROM "aws_athena_query_history"
   ```

2. **Set workgroup limits**
   ```python
   athena.update_workgroup(
       WorkGroup='analytics',
       ConfigurationUpdates={
           'BytesScannedCutoffPerQuery': 10737418240  # 10GB
       }
   )
   ```

3. **Use views for common queries**
   ```sql
   CREATE OR REPLACE VIEW recent_events AS
   SELECT * FROM events
   WHERE year='2024' AND month='01';
   ```

### EMR Costs

1. **Use Spot Instances**
   - Master: On-Demand
   - Core: On-Demand or Spot (60% discount)
   - Task: Spot (90% discount)

2. **Auto-terminate clusters**
   ```python
   cluster_config = {
       'AutoTerminationPolicy': {
           'IdleTimeout': 3600  # 1 hour
       }
   }
   ```

3. **Right-size instances**
   - Start small, scale up if needed
   - Monitor CPU/Memory utilization
   - Use m5.xlarge for general workloads

## Security Best Practices

### Encryption

1. **Enable encryption everywhere**
   - S3: SSE-KMS
   - Glue: KMS for metadata
   - EMR: Encryption in-transit and at-rest
   - Athena: Encrypt query results

2. **Use separate KMS keys**
   - One key per environment
   - Rotate keys regularly
   - Use key policies for access control

### Access Control

1. **Principle of Least Privilege**
   ```json
   {
     "Effect": "Allow",
     "Action": [
       "glue:GetDatabase",
       "glue:GetTable"
     ],
     "Resource": "arn:aws:glue:*:*:catalog/database/analytics"
   }
   ```

2. **Use separate roles**
   - Glue crawler role
   - EMR service role
   - EMR EC2 instance profile
   - Athena execution role

3. **Implement tagging strategy**
   ```python
   tags = {
       'Environment': 'production',
       'DataClassification': 'confidential',
       'Owner': 'data-engineering',
       'CostCenter': 'analytics'
   }
   ```

### Audit and Compliance

1. **Enable CloudTrail**
   - Log all API calls
   - Store in separate bucket
   - Enable log file validation

2. **Monitor access patterns**
   - Review CloudWatch Logs
   - Set up anomaly detection
   - Alert on unusual activity

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Glue Crawlers**
   - Tables created/updated
   - Crawl duration
   - DPU hours used

2. **Athena**
   - Query execution time
   - Data scanned per query
   - Failed queries

3. **EMR**
   - Cluster utilization
   - Job duration
   - Failed steps

### CloudWatch Alarms

```python
# High query failure rate
cloudwatch.put_metric_alarm(
    AlarmName='athena-high-failure-rate',
    MetricName='FailedQueries',
    Namespace='AWS/Athena',
    Statistic='Sum',
    Period=300,
    EvaluationPeriods=2,
    Threshold=10,
    ComparisonOperator='GreaterThanThreshold'
)
```

## Testing and Validation

### Data Quality Checks

```python
# Validate schema
expected_schema = ['id', 'name', 'created_at']
actual_schema = df.columns
assert set(expected_schema) == set(actual_schema)

# Check for nulls
null_count = df.filter(col('id').isNull()).count()
assert null_count == 0, f"Found {null_count} null IDs"

# Validate data ranges
invalid_dates = df.filter(col('created_at') > current_timestamp()).count()
assert invalid_dates == 0, "Future dates found"
```

### Integration Testing

```python
def test_end_to_end_pipeline():
    # 1. Create test data
    test_data = create_test_dataset()
    
    # 2. Upload to S3
    upload_to_s3(test_data, 's3://test-bucket/data/')
    
    # 3. Run crawler
    run_crawler('test-crawler')
    
    # 4. Verify table created
    table = catalog.get_table('test_db', 'test_table')
    assert table is not None
    
    # 5. Query data
    results = athena.execute_query('SELECT COUNT(*) FROM test_table')
    assert results[0]['count'] == len(test_data)
    
    # 6. Cleanup
    cleanup_test_resources()
```

## Disaster Recovery

### Backup Strategy

1. **Glue Catalog**
   ```python
   # Export catalog metadata
   backup_catalog_to_s3(
       output_bucket='backup-bucket',
       databases=['raw_data', 'processed', 'analytics']
   )
   ```

2. **S3 Data**
   - Enable versioning
   - Cross-region replication
   - Regular snapshots

3. **Infrastructure**
   - Store Terraform state in S3
   - Version control all code
   - Document manual steps

### Recovery Procedures

1. **Restore Glue Catalog**
   ```bash
   aws glue import-catalog-from-glue \
     --source-catalog-id 123456789012 \
     --target-catalog-id 987654321098
   ```

2. **Restore S3 Data**
   ```bash
   aws s3 sync s3://backup-bucket/ s3://primary-bucket/ \
     --source-region us-west-2 \
     --region us-east-1
   ```

## Performance Benchmarks

### File Size Guidelines

- **Optimal file size**: 128MB - 1GB
- **Minimum file size**: 10MB
- **Too many files**: > 10,000 per partition

### Query Performance Targets

- **Interactive queries**: < 10 seconds
- **Batch queries**: < 5 minutes
- **ETL jobs**: Monitor against baseline

### Monitoring Tools

- CloudWatch Dashboards
- Athena Query History
- EMR Application History
- Custom metrics via boto3

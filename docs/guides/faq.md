# Frequently Asked Questions (FAQ)

## General Questions

### Q: What is centralized metadata management?
**A:** Centralized metadata management provides a single source of truth for all data catalog information. Instead of maintaining separate metadata stores for different tools (Hive, Spark, Athena), AWS Glue Data Catalog acts as a unified repository that all services can use.

### Q: Why use AWS Glue Data Catalog instead of Hive Metastore?
**A:** AWS Glue Data Catalog offers several advantages:
- Fully managed service (no infrastructure to maintain)
- Integrated with multiple AWS services (EMR, Athena, Redshift Spectrum)
- Automatic schema discovery with crawlers
- Built-in version control for schemas
- Better scalability and availability

### Q: What are the costs involved?
**A:** Main cost components:
- **Glue Data Catalog**: First million objects free, then $1 per 100,000 objects per month
- **Glue Crawlers**: $0.44 per DPU-Hour (minimum 10 minutes)
- **EMR**: EC2 instance costs + EMR service fees
- **Athena**: $5 per TB of data scanned
- **S3**: Storage and request costs

## Implementation Questions

### Q: How do I migrate from Hive Metastore to Glue Data Catalog?
**A:** Migration options:
1. **Automated**: Use Glue crawlers to discover existing data
2. **Manual**: Use `aws glue import-catalog-to-glue` command
3. **Programmatic**: Use Python scripts with boto3

Example:
```bash
aws glue import-catalog-to-glue \
  --catalog-id 123456789012 \
  --region us-east-1
```

### Q: Can I use both Hive Metastore and Glue Catalog simultaneously?
**A:** Yes, but it's not recommended. You can configure EMR to use Glue for some tables and Hive for others, but this adds complexity. Better to fully migrate to Glue.

### Q: How do I handle schema evolution?
**A:** Glue supports schema evolution:
- Crawlers can detect and update schema changes
- Use `UPDATE_IN_DATABASE` for crawler schema change policy
- Table versioning tracks all schema changes
- Can rollback to previous versions if needed

### Q: What data formats are supported?
**A:** Supported formats:
- **Columnar**: Parquet, ORC
- **Row-based**: JSON, CSV, TSV, Avro
- **Semi-structured**: XML
- **Custom**: Define custom classifiers

## Performance Questions

### Q: How can I optimize Athena query costs?
**A:** Cost optimization strategies:
1. **Partition data** by frequently filtered columns (e.g., date)
2. **Use columnar formats** (Parquet recommended)
3. **Compress data** (Snappy for Parquet)
4. **Select only needed columns** (avoid SELECT *)
5. **Set query result reuse** in workgroups
6. **Use workgroup data scan limits**

### Q: Why are my Athena queries slow?
**A:** Common causes and solutions:
- **Large files**: Optimal file size 128MB-1GB
- **Too many small files**: Combine files
- **Wrong format**: Use Parquet instead of JSON/CSV
- **Missing partitions**: Add partition pruning
- **Complex JOINs**: Optimize join order

### Q: How do I optimize EMR cluster performance?
**A:** Performance tuning:
1. **Right-size instances**: Use m5/r5 families
2. **Enable auto-scaling**: Scale based on YARN metrics
3. **Use Spot instances**: For task nodes (60-90% cost savings)
4. **Optimize Spark config**: Tune executor memory and cores
5. **Use instance fleets**: Mix instance types for availability

## Security Questions

### Q: How is data encrypted?
**A:** Encryption layers:
- **S3**: SSE-KMS or SSE-S3 encryption at rest
- **Glue Catalog**: KMS encryption for metadata
- **EMR**: Encryption in-transit and at-rest
- **Athena**: Query results encrypted in S3

### Q: How do I control access to tables?
**A:** Access control methods:
1. **IAM policies**: Control who can access Glue/Athena
2. **S3 bucket policies**: Control data access
3. **Lake Formation**: Fine-grained permissions (column/row level)
4. **Resource policies**: Share across accounts

### Q: Can I use this with multiple AWS accounts?
**A:** Yes, using:
- **Glue resource policies**: Share catalog cross-account
- **Lake Formation**: Centralized governance
- **S3 bucket policies**: Grant cross-account access
- **IAM roles**: Assume role for cross-account access

## Troubleshooting Questions

### Q: Crawler found no tables, why?
**A:** Common causes:
1. **No data files**: Ensure data exists in S3 path
2. **Permissions**: Glue role needs S3 read access
3. **Unsupported format**: Check file format
4. **Empty folders**: Crawlers need actual files
5. **Wrong path**: Verify S3 path is correct

### Q: Table exists but Athena query fails?
**A:** Check:
1. **Table location**: Verify S3 path in table properties
2. **Permissions**: Query execution role needs S3 access
3. **File format**: Ensure SerDe matches actual format
4. **Partitions**: Run `MSCK REPAIR TABLE` if needed
5. **Encryption**: Consistent encryption settings

### Q: EMR cluster fails to start?
**A:** Common issues:
1. **Subnet**: Ensure EMR subnet has internet access
2. **Security groups**: Check required ports are open
3. **IAM roles**: Verify EMR service role and instance profile
4. **Limits**: Check EC2 instance limits
5. **Bootstrap**: Review bootstrap action logs

## Advanced Questions

### Q: Can I use this with real-time data?
**A:** Yes, with modifications:
- Use **Kinesis Firehose** to write to S3
- Enable **Glue streaming ETL** for real-time processing
- Use **Athena** for near real-time queries
- Consider **partition projection** for time-series data

### Q: How do I implement data lineage?
**A:** Lineage tracking options:
1. **CloudTrail**: Track API calls
2. **Glue Job bookmarks**: Track processed data
3. **Custom metadata**: Add lineage info to table parameters
4. **Lake Formation**: Built-in lineage tracking

### Q: Can I use custom data classifiers?
**A:** Yes, create custom classifiers:
- **Grok**: Pattern matching for log files
- **JSON**: Custom JSON path expressions
- **CSV**: Custom delimiter/quote characters
- **XML**: XPath expressions

Example:
```python
glue.create_classifier(
    GrokClassifier={
        'Name': 'custom-logs',
        'Classification': 'logs',
        'GrokPattern': '%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}'
    }
)
```

## Best Practices

### Q: What are the top 5 best practices?
**A:**
1. **Partition wisely**: Use date partitioning (year/month/day)
2. **Use Parquet**: Best format for analytics
3. **Implement lifecycle policies**: Archive old data to Glacier
4. **Monitor costs**: Set up billing alarms
5. **Test in dev**: Always test changes in non-prod first

### Q: How should I organize my S3 data lake?
**A:** Recommended structure:
```
s3://my-datalake/
├── raw/              # Raw, unprocessed data
│   ├── source1/
│   └── source2/
├── processed/        # Cleaned, validated data
│   ├── dataset1/
│   └── dataset2/
├── curated/          # Analytics-ready data
│   ├── reports/
│   └── aggregates/
└── archive/          # Historical data
```

### Q: How often should crawlers run?
**A:** Depends on data freshness needs:
- **Batch data**: Daily or weekly
- **Streaming**: Hourly or on-demand
- **Static data**: On-demand only
- **Partitioned data**: After new partitions added

## Getting Help

### Q: Where can I find more information?
**A:**
- AWS Glue Documentation: https://docs.aws.amazon.com/glue/
- Amazon Athena Guide: https://docs.aws.amazon.com/athena/
- Amazon EMR Guide: https://docs.aws.amazon.com/emr/
- This repository's documentation in `/docs` folder

### Q: How do I report issues?
**A:**
1. Check troubleshooting guide first
2. Review CloudWatch logs
3. Open GitHub issue with:
   - Error messages
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs

# Athena Query Examples

This directory contains example SQL queries for Amazon Athena.

## Basic Queries

### Create Database
```sql
CREATE DATABASE IF NOT EXISTS analytics
COMMENT 'Analytics database'
LOCATION 's3://my-bucket/analytics/';
```

### Create Table
```sql
CREATE EXTERNAL TABLE IF NOT EXISTS analytics.user_events (
    event_id STRING,
    user_id STRING,
    event_type STRING,
    timestamp TIMESTAMP,
    properties STRING
)
PARTITIONED BY (
    year STRING,
    month STRING,
    day STRING
)
STORED AS PARQUET
LOCATION 's3://my-bucket/processed/user_events/'
TBLPROPERTIES (
    'parquet.compression'='SNAPPY',
    'has_encrypted_data'='true'
);
```

### Add Partitions
```sql
-- Single partition
ALTER TABLE analytics.user_events
ADD PARTITION (year='2024', month='01', day='15')
LOCATION 's3://my-bucket/processed/user_events/year=2024/month=01/day=15/';

-- Multiple partitions
MSCK REPAIR TABLE analytics.user_events;
```

## Analytical Queries

### Daily Active Users
```sql
SELECT 
    CONCAT(year, '-', month, '-', day) as date,
    COUNT(DISTINCT user_id) as daily_active_users
FROM analytics.user_events
WHERE year = '2024' 
    AND month = '01'
GROUP BY year, month, day
ORDER BY date;
```

### Event Type Distribution
```sql
SELECT 
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM analytics.user_events
WHERE year = '2024'
GROUP BY event_type
ORDER BY event_count DESC;
```

### Top Users by Activity
```sql
SELECT 
    user_id,
    COUNT(*) as total_events,
    COUNT(DISTINCT event_type) as distinct_events,
    MIN(timestamp) as first_event,
    MAX(timestamp) as last_event
FROM analytics.user_events
WHERE year = '2024'
GROUP BY user_id
ORDER BY total_events DESC
LIMIT 100;
```

## Advanced Queries

### CTAS - Create Optimized Table
```sql
CREATE TABLE analytics.daily_summary
WITH (
    format = 'PARQUET',
    parquet_compression = 'SNAPPY',
    partitioned_by = ARRAY['year', 'month']
) AS
SELECT 
    DATE(timestamp) as event_date,
    user_id,
    event_type,
    COUNT(*) as event_count,
    YEAR(DATE(timestamp)) as year,
    MONTH(DATE(timestamp)) as month
FROM analytics.user_events
WHERE year = '2024'
GROUP BY 
    DATE(timestamp),
    user_id,
    event_type,
    YEAR(DATE(timestamp)),
    MONTH(DATE(timestamp));
```

### Views
```sql
-- Create view for recent events
CREATE OR REPLACE VIEW analytics.recent_events AS
SELECT *
FROM analytics.user_events
WHERE year = CAST(YEAR(CURRENT_DATE) AS VARCHAR)
    AND month = LPAD(CAST(MONTH(CURRENT_DATE) AS VARCHAR), 2, '0');

-- Query the view
SELECT event_type, COUNT(*) as count
FROM analytics.recent_events
GROUP BY event_type;
```

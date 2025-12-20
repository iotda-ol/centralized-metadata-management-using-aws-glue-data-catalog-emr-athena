-- Amazon Athena Query Examples with AWS Glue Data Catalog
-- These examples demonstrate common SQL patterns using Athena with centralized metadata

-- ============================================================================
-- DATABASE OPERATIONS
-- ============================================================================

-- Show all databases in the catalog
SHOW DATABASES;

-- Use a specific database
USE centralized_metadata_db;

-- Show all tables in current database
SHOW TABLES;

-- ============================================================================
-- TABLE EXPLORATION
-- ============================================================================

-- Describe table structure
DESCRIBE sales;

-- Show detailed table information
SHOW CREATE TABLE sales;

-- Show table partitions
SHOW PARTITIONS sales;

-- Get column statistics
SHOW COLUMNS FROM sales;

-- ============================================================================
-- BASIC QUERIES
-- ============================================================================

-- Simple SELECT with LIMIT
SELECT *
FROM sales
LIMIT 10;

-- SELECT specific columns
SELECT 
    customer_id,
    product_name,
    amount,
    transaction_date
FROM sales
LIMIT 100;

-- WHERE clause filtering
SELECT *
FROM sales
WHERE amount > 1000
  AND year = '2024'
LIMIT 50;

-- ============================================================================
-- PARTITION QUERIES (Optimized for Performance)
-- ============================================================================

-- Query specific partition (much faster)
SELECT 
    customer_id,
    product_name,
    SUM(amount) as total_amount
FROM sales
WHERE year = '2024' 
  AND month = '01'
GROUP BY customer_id, product_name;

-- Query multiple partitions
SELECT 
    year,
    month,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue
FROM sales
WHERE year = '2024'
  AND month IN ('01', '02', '03')
GROUP BY year, month
ORDER BY year, month;

-- ============================================================================
-- AGGREGATIONS
-- ============================================================================

-- Basic aggregations
SELECT 
    COUNT(*) as total_transactions,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction,
    MIN(amount) as min_transaction,
    MAX(amount) as max_transaction
FROM sales
WHERE year = '2024';

-- Group by with aggregations
SELECT 
    category,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_revenue,
    MIN(amount) as min_revenue,
    MAX(amount) as max_revenue
FROM sales
WHERE year = '2024'
GROUP BY category
ORDER BY total_revenue DESC;

-- ============================================================================
-- WINDOW FUNCTIONS
-- ============================================================================

-- Ranking customers by revenue
SELECT 
    customer_id,
    SUM(amount) as total_revenue,
    RANK() OVER (ORDER BY SUM(amount) DESC) as revenue_rank,
    ROW_NUMBER() OVER (ORDER BY SUM(amount) DESC) as row_num
FROM sales
WHERE year = '2024'
GROUP BY customer_id
LIMIT 10;

-- Running total by date
SELECT 
    transaction_date,
    amount,
    SUM(amount) OVER (
        ORDER BY transaction_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total
FROM sales
WHERE year = '2024' AND month = '01'
ORDER BY transaction_date;

-- ============================================================================
-- JOINS
-- ============================================================================

-- Inner join between sales and customers
SELECT 
    s.transaction_id,
    s.customer_id,
    c.customer_name,
    c.customer_email,
    s.amount,
    s.transaction_date
FROM sales s
INNER JOIN customers c ON s.customer_id = c.customer_id
WHERE s.year = '2024' AND s.month = '01'
LIMIT 100;

-- Left join with aggregation
SELECT 
    c.customer_id,
    c.customer_name,
    COALESCE(SUM(s.amount), 0) as total_spent,
    COUNT(s.transaction_id) as transaction_count
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
    AND s.year = '2024'
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC;

-- ============================================================================
-- SUBQUERIES AND CTEs
-- ============================================================================

-- Common Table Expression (CTE)
WITH monthly_sales AS (
    SELECT 
        year,
        month,
        SUM(amount) as monthly_revenue,
        COUNT(*) as monthly_transactions
    FROM sales
    WHERE year = '2024'
    GROUP BY year, month
)
SELECT 
    year,
    month,
    monthly_revenue,
    monthly_transactions,
    monthly_revenue / monthly_transactions as avg_transaction_value
FROM monthly_sales
ORDER BY year, month;

-- Multiple CTEs
WITH customer_stats AS (
    SELECT 
        customer_id,
        COUNT(*) as purchase_count,
        SUM(amount) as total_spent,
        AVG(amount) as avg_spent
    FROM sales
    WHERE year = '2024'
    GROUP BY customer_id
),
customer_segments AS (
    SELECT 
        customer_id,
        purchase_count,
        total_spent,
        CASE 
            WHEN total_spent > 10000 THEN 'Premium'
            WHEN total_spent > 5000 THEN 'Gold'
            WHEN total_spent > 1000 THEN 'Silver'
            ELSE 'Bronze'
        END as customer_segment
    FROM customer_stats
)
SELECT 
    customer_segment,
    COUNT(*) as customer_count,
    SUM(total_spent) as segment_revenue,
    AVG(total_spent) as avg_customer_value
FROM customer_segments
GROUP BY customer_segment
ORDER BY segment_revenue DESC;

-- ============================================================================
-- DATE AND TIME OPERATIONS
-- ============================================================================

-- Extract date parts
SELECT 
    transaction_date,
    date_format(transaction_date, '%Y-%m-%d') as formatted_date,
    year(transaction_date) as txn_year,
    month(transaction_date) as txn_month,
    day(transaction_date) as txn_day,
    day_of_week(transaction_date) as day_of_week
FROM sales
WHERE year = '2024' AND month = '01'
LIMIT 10;

-- Date range filtering
SELECT 
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue
FROM sales
WHERE transaction_date BETWEEN DATE '2024-01-01' AND DATE '2024-01-31';

-- ============================================================================
-- STRING OPERATIONS
-- ============================================================================

-- String functions
SELECT 
    customer_id,
    product_name,
    UPPER(product_name) as uppercase_name,
    LOWER(product_name) as lowercase_name,
    LENGTH(product_name) as name_length,
    SUBSTR(product_name, 1, 10) as short_name
FROM sales
WHERE year = '2024'
LIMIT 10;

-- Pattern matching
SELECT 
    product_name,
    COUNT(*) as sales_count
FROM sales
WHERE product_name LIKE '%laptop%'
  AND year = '2024'
GROUP BY product_name;

-- ============================================================================
-- CREATING TABLES (CTAS - Create Table As Select)
-- ============================================================================

-- Create a summary table
CREATE TABLE sales_monthly_summary
WITH (
    format = 'PARQUET',
    parquet_compression = 'SNAPPY',
    external_location = 's3://your-bucket/summaries/sales_monthly/'
) AS
SELECT 
    year,
    month,
    category,
    COUNT(*) as transaction_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_transaction,
    MIN(amount) as min_transaction,
    MAX(amount) as max_transaction
FROM sales
GROUP BY year, month, category;

-- Create partitioned table
CREATE TABLE sales_by_year
WITH (
    format = 'PARQUET',
    partitioned_by = ARRAY['year'],
    external_location = 's3://your-bucket/sales_by_year/'
) AS
SELECT 
    customer_id,
    product_name,
    amount,
    transaction_date,
    year
FROM sales;

-- ============================================================================
-- INSERT INTO
-- ============================================================================

-- Insert query results into existing table
INSERT INTO sales_summary
SELECT 
    customer_id,
    SUM(amount) as total_spent,
    COUNT(*) as purchase_count
FROM sales
WHERE year = '2024' AND month = '01'
GROUP BY customer_id;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Create a view
CREATE OR REPLACE VIEW high_value_customers AS
SELECT 
    customer_id,
    SUM(amount) as total_spent,
    COUNT(*) as purchase_count,
    AVG(amount) as avg_purchase
FROM sales
WHERE year = '2024'
GROUP BY customer_id
HAVING SUM(amount) > 10000;

-- Query the view
SELECT * FROM high_value_customers
ORDER BY total_spent DESC
LIMIT 10;

-- ============================================================================
-- PERFORMANCE OPTIMIZATION TIPS
-- ============================================================================

-- 1. Always use partition filters when possible
-- GOOD:
SELECT * FROM sales WHERE year = '2024' AND month = '01';

-- BAD (scans all partitions):
-- SELECT * FROM sales WHERE amount > 1000;

-- 2. Use columnar formats (Parquet, ORC)
-- Already configured in table creation

-- 3. Use appropriate compression
-- Configured as SNAPPY in CTAS examples

-- 4. Limit result sets
-- Use LIMIT for exploratory queries
SELECT * FROM sales LIMIT 100;

-- 5. Use approximate functions for faster results
SELECT 
    approx_distinct(customer_id) as approx_unique_customers,
    approx_percentile(amount, 0.5) as median_amount
FROM sales
WHERE year = '2024';

-- ============================================================================
-- MAINTENANCE OPERATIONS
-- ============================================================================

-- Add new partition manually
ALTER TABLE sales ADD IF NOT EXISTS
PARTITION (year='2024', month='02')
LOCATION 's3://your-bucket/data/sales/year=2024/month=02/';

-- Drop partition
ALTER TABLE sales DROP IF EXISTS PARTITION (year='2023', month='01');

-- Update table properties
ALTER TABLE sales SET TBLPROPERTIES ('description' = 'Sales transaction data');

-- ============================================================================
-- TROUBLESHOOTING QUERIES
-- ============================================================================

-- Check table size
SELECT 
    SUM("$path" IS NOT NULL) as file_count
FROM sales;

-- Check partition distribution
SELECT 
    year,
    month,
    COUNT(*) as record_count
FROM sales
GROUP BY year, month
ORDER BY year DESC, month DESC;

-- Verify data types
DESCRIBE sales;

-- Check for null values
SELECT 
    COUNT(*) as total_rows,
    COUNT(customer_id) as non_null_customer_id,
    COUNT(amount) as non_null_amount,
    COUNT(*) - COUNT(customer_id) as null_customer_id,
    COUNT(*) - COUNT(amount) as null_amount
FROM sales
WHERE year = '2024';

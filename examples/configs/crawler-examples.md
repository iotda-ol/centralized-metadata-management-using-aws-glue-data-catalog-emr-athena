# Example Glue Crawler Configuration

This example demonstrates how to configure crawlers for automatic schema discovery.

## Basic Crawler Configuration

```python
from metadata_mgmt.glue.catalog_manager import CatalogManager
import boto3

glue = boto3.client('glue')

# Create crawler for raw data
crawler_config = {
    'Name': 'raw-events-crawler',
    'Role': 'arn:aws:iam::123456789012:role/GlueServiceRole',
    'DatabaseName': 'raw_data',
    'Targets': {
        'S3Targets': [
            {
                'Path': 's3://my-bucket/raw/events/',
                'Exclusions': ['*.tmp', '_*']
            }
        ]
    },
    'SchemaChangePolicy': {
        'UpdateBehavior': 'UPDATE_IN_DATABASE',
        'DeleteBehavior': 'LOG'
    },
    'Schedule': 'cron(0 2 * * ? *)',  # Daily at 2 AM UTC
    'Configuration': '''
    {
        "Version": 1.0,
        "CrawlerOutput": {
            "Partitions": {
                "AddOrUpdateBehavior": "InheritFromTable"
            }
        }
    }
    '''
}

glue.create_crawler(**crawler_config)
```

## Crawler with Custom Classifier

```python
# Create custom classifier for JSON logs
classifier_config = {
    'Name': 'json-logs-classifier',
    'JsonClassifier': {
        'JsonPath': '$.records[*]'
    }
}

glue.create_classifier(**classifier_config)

# Use classifier in crawler
crawler_with_classifier = {
    'Name': 'logs-crawler',
    'Role': 'arn:aws:iam::123456789012:role/GlueServiceRole',
    'DatabaseName': 'raw_data',
    'Classifiers': ['json-logs-classifier'],
    'Targets': {
        'S3Targets': [
            {'Path': 's3://my-bucket/logs/'}
        ]
    }
}

glue.create_crawler(**crawler_with_classifier)
```

## Multiple S3 Targets

```python
# Crawler for multiple paths
multi_target_crawler = {
    'Name': 'multi-source-crawler',
    'Role': 'arn:aws:iam::123456789012:role/GlueServiceRole',
    'DatabaseName': 'raw_data',
    'Targets': {
        'S3Targets': [
            {'Path': 's3://bucket1/data/'},
            {'Path': 's3://bucket2/data/'},
            {'Path': 's3://bucket3/data/'}
        ]
    }
}

glue.create_crawler(**multi_target_crawler)
```

## Start Crawler Programmatically

```python
import boto3
import time

glue = boto3.client('glue')

def run_crawler(crawler_name):
    """Start crawler and wait for completion"""
    # Start crawler
    glue.start_crawler(Name=crawler_name)
    print(f"Started crawler: {crawler_name}")
    
    # Wait for completion
    while True:
        response = glue.get_crawler(Name=crawler_name)
        state = response['Crawler']['State']
        
        if state == 'READY':
            print("Crawler completed")
            break
        elif state in ['STOPPING', 'STOPPED']:
            print("Crawler stopped")
            break
            
        print(f"Crawler state: {state}")
        time.sleep(10)
    
    # Get metrics
    metrics = glue.get_crawler_metrics(CrawlerNameList=[crawler_name])
    print(f"Tables created/updated: {metrics['CrawlerMetricsList'][0]['TablesCreated']}")

# Run the crawler
run_crawler('raw-events-crawler')
```

## Terraform Configuration

```hcl
# terraform/environments/dev/terraform.tfvars

glue_crawlers = {
  raw_events = {
    database        = "raw_data"
    s3_targets      = ["s3://my-bucket/raw/events/"]
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
    schedule        = "cron(0 2 * * ? *)"
  }
  
  raw_users = {
    database        = "raw_data"
    s3_targets      = ["s3://my-bucket/raw/users/"]
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
    schedule        = "cron(0 3 * * ? *)"
  }
}
```

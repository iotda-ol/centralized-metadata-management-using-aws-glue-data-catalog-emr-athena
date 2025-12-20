/**
 * Amazon EMR Module
 * Creates and manages EMR clusters for big data processing
 */

resource "aws_emr_cluster" "main" {
  name          = "${var.project_name}-${var.environment}-emr-cluster"
  release_label = var.emr_release_label
  applications  = var.applications

  service_role = var.service_role_arn

  ec2_attributes {
    instance_profile                  = var.instance_profile_arn
    emr_managed_master_security_group = var.master_security_group_id
    emr_managed_slave_security_group  = var.slave_security_group_id
    subnet_id                         = var.subnet_id
    key_name                          = var.key_name
  }

  master_instance_group {
    instance_type  = var.master_instance_type
    instance_count = 1
    name           = "Master"

    ebs_config {
      size                 = var.master_ebs_size
      type                 = "gp3"
      volumes_per_instance = 1
    }
  }

  core_instance_group {
    instance_type  = var.core_instance_type
    instance_count = var.core_instance_count
    name           = "Core"

    ebs_config {
      size                 = var.core_ebs_size
      type                 = "gp3"
      volumes_per_instance = 1
    }

    autoscaling_policy = var.enable_autoscaling ? jsonencode({
      Constraints = {
        MinCapacity = var.core_instance_count
        MaxCapacity = var.core_max_instance_count
      }
      Rules = [
        {
          Name   = "Scale-up-on-YARNMemory"
          Action = {
            SimpleScalingPolicyConfiguration = {
              AdjustmentType         = "CHANGE_IN_CAPACITY"
              ScalingAdjustment      = 1
              CoolDown               = 300
            }
          }
          Trigger = {
            CloudWatchAlarmDefinition = {
              ComparisonOperator = "LESS_THAN"
              EvaluationPeriods  = 1
              MetricName         = "YARNMemoryAvailablePercentage"
              Namespace          = "AWS/ElasticMapReduce"
              Period             = 300
              Statistic          = "AVERAGE"
              Threshold          = 15.0
              Unit               = "PERCENT"
            }
          }
        }
      ]
    }) : null
  }

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
    },
    {
      Classification = "spark-defaults"
      Properties = {
        "spark.sql.catalogImplementation" = "hive"
      }
    }
  ])

  dynamic "bootstrap_action" {
    for_each = var.bootstrap_actions
    content {
      name = bootstrap_action.value.name
      path = bootstrap_action.value.path
      args = lookup(bootstrap_action.value, "args", [])
    }
  }

  log_uri = var.log_uri

  termination_protection            = var.termination_protection
  keep_job_flow_alive_when_no_steps = var.keep_alive

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-emr-cluster"
      Environment = var.environment
    }
  )
}

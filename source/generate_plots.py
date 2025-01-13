import boto3
import json
import os
from datetime import datetime

TABLE_NAME = os.getenv("TABLE_NAME")

# AWS Clients
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)
    
    response = table.scan()
    items = response['Items']
    
    anomaly_count = {}
    site_energy_data = {}

    # Process data
    for item in items:
        site_id = item['site_id']
        energy_generated = float(item.get('energy_generated_kwh', 0))
        energy_consumed = float(item.get('energy_consumed_kwh', 0))
        anomaly = item.get('anomaly', False)
        timestamp = item.get('timestamp', datetime.utcnow().isoformat())
        
        # Publish energy generated and consumed metrics to CloudWatch
        cloudwatch.put_metric_data(
            Namespace="EnergyMetrics",
            MetricData=[
                {
                    'MetricName': 'EnergyGenerated',
                    'Dimensions': [{'Name': 'SiteID', 'Value': site_id}],
                    'Value': energy_generated,
                    'Unit': 'None',
                    'Timestamp': datetime.fromisoformat(timestamp)
                },
                {
                    'MetricName': 'EnergyConsumed',
                    'Dimensions': [{'Name': 'SiteID', 'Value': site_id}],
                    'Value': energy_consumed,
                    'Unit': 'None',
                    'Timestamp': datetime.fromisoformat(timestamp)
                }
            ]
        )

        # Count anomalies
        if anomaly:
            anomaly_count[site_id] = anomaly_count.get(site_id, 0) + 1

        # Aggregate energy data
        if site_id not in site_energy_data:
            site_energy_data[site_id] = {"generated": 0, "consumed": 0}
        
        site_energy_data[site_id]["generated"] += energy_generated
        site_energy_data[site_id]["consumed"] += energy_consumed
    
    # Publish energy metrics
    for site_id, data in site_energy_data.items():
        cloudwatch.put_metric_data(
            Namespace="EnergyMetrics",
            MetricData=[
                {
                    'MetricName': 'SiteEnergyGenerated',
                    'Dimensions': [{'Name': 'SiteID', 'Value': site_id}],
                    'Value': data["generated"],
                    'Unit': 'None'
                },
                {
                    'MetricName': 'SiteEnergyConsumed',
                    'Dimensions': [{'Name': 'SiteID', 'Value': site_id}],
                    'Value': data["consumed"],
                    'Unit': 'None'
                }
            ]
        )
    
    # Publish anomaly metrics
    for site_id, count in anomaly_count.items():
        cloudwatch.put_metric_data(
            Namespace="EnergyMetrics",
            MetricData=[
                {
                    'MetricName': 'Anomalies',
                    'Dimensions': [{'Name': 'SiteID', 'Value': site_id}],
                    'Value': count,
                    'Unit': 'Count'
                }
            ]
        )
    
    return {
        "statusCode": 200,
        "body": json.dumps("Metrics published to CloudWatch.")
    }

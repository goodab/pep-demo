import boto3
import json
import time
import random
import os
from datetime import datetime

REGION = os.getenv("REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")
NUM_SITES = int(os.getenv("NUM_SITES"))
MAX_GEN_ENERGY_KWH = float(os.getenv("MAX_GEN_ENERGY_KWH"))
MIN_GEN_ENERGY_KWH = float(os.getenv("MIN_GEN_ENERGY_KWH"))
MAX_CONSUMED_ENERGY_KWH = float(os.getenv("MAX_CONSUMED_ENERGY_KWH"))
MIN_CONSUMED_ENERGY_KWH = float(os.getenv("MIN_CONSUMED_ENERGY_KWH"))


# Initialize S3 client
s3 = boto3.client("s3", region_name=REGION)

def generate_random_data(site_id):
    """Generate random data for a single site."""
    return {
        "site_id": site_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "energy_generated_kwh": round(random.uniform(MIN_GEN_ENERGY_KWH, MAX_GEN_ENERGY_KWH), 2),
        "energy_consumed_kwh": round(random.uniform(MIN_CONSUMED_ENERGY_KWH, MAX_CONSUMED_ENERGY_KWH), 2),
    }

def generate_data_feed():
    """Generate random data for multiple energy sites."""
    return [
        generate_random_data(site_id=f"site_{i+1}") for i in range(NUM_SITES)
    ]

def upload_to_s3(data, bucket_name, key):
    """Upload JSON data to the specified S3 bucket."""
    json_data = json.dumps(data, indent=4)
    s3.put_object(Bucket=bucket_name, Key=key, Body=json_data)
    print(f"Uploaded {key} to {bucket_name}")

def lambda_handler(event, context):
    """Simulate live data feed by generating and uploading JSON files."""
    # Generate data
    data_feed = generate_data_feed()

    # Generate unique filename based on the timestamp
    filename = f"data_feed_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

    # Upload data to S3
    upload_to_s3(data_feed, BUCKET_NAME, filename)

import json
import os
import boto3
from decimal import Decimal

REGION = os.getenv("REGION")
TABLE_NAME = os.getenv("TABLE_NAME")

def lambda_handler(event, context):
    """
    Process an uploaded JSON file in S3, calculate net energy, and identify anomalies.
    """
    # Initialize S3 client
    s3 = boto3.client("s3", region_name=REGION)
    lambda_client = boto3.client("lambda")

    # Initialize DynamoDB client
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    # Get bucket and object key from the event
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    object_key = event["Records"][0]["s3"]["object"]["key"]

    print(f"{bucket_name=} {object_key=}")

    try:
        # Retrieve the file content from S3
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response["Body"].read().decode("utf-8")

        # Parse JSON content
        data = json.loads(file_content)
        processed_records = []

        print(f"{len(data)=}")

        for record in data:
            # Calculate net energy
            energy_generated = record.get("energy_generated_kwh", 0)
            energy_consumed = record.get("energy_consumed_kwh", 0)
            net_energy = energy_generated - energy_consumed

            # Identify anomalies
            anomaly = (energy_generated < 0) or (energy_consumed < 0)

            # Append processed record
            processed_record = {
                "site_id": record.get("site_id"),
                "timestamp": record.get("timestamp"),
                "energy_generated_kwh": round(Decimal(energy_generated), 3),
                "energy_consumed_kwh": round(Decimal(energy_consumed), 3),
                "net_energy_kwh": round(Decimal(net_energy), 3),
                "anomaly": anomaly,
            }
            print(f"{processed_record=}")
            processed_records.append(processed_record)

        with table.batch_writer() as batch:
            for record in processed_records:
                batch.put_item(Item=record)
        print("Success")
        lambda_client.invoke(FunctionName="generate_metrics",
                             InvocationType="Event",
                             Payload=json.dumps({}))
        return {"statusCode": 200, "body": "File processed successfully."}

    except Exception as e:
        print(f"Error processing file: {e}")
        raise e
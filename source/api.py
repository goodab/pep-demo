from fastapi import FastAPI
import datetime
import boto3
import os
from boto3.dynamodb.conditions import Attr

app = FastAPI()

TABLE_NAME = os.getenv("TABLE_NAME")
QUERY_LIMIT = os.getenv("QUERY_LIMIT", 100)

@app.get("/site_entries/{item_id}")
async def read_item(item_id, start: datetime.datetime, end: datetime.datetime):
    """
    Return all energy generation/consumption entries for site site_id between datetimes start and end.
    """
    if not end:
        end = datetime.datetime.utcnow()
    if not start:
        start = datetime.datetime.utcnow()
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    return table.query(IndexName="site_id",
                Select = "ALL_ATTRIBUTES",
                limit = QUERY_LIMIT,
                ConsistentRead = False,
                FilterExpression = Attr("timestamp").gt(end).lt(start))["Items"]

@app.get("/anomaly/{site_id}")
async def get_anomaly(site_id):
    """
    Gets all anomalies for site site_id.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)
    return table.query(IndexName="site_id", 
                limit = QUERY_LIMIT,
                Select = "ALL_ATTRIBUTES",
                ConsistentRead = False,
                FilterExpression = Attr("anomaly").eq(True)
                )["Items"]
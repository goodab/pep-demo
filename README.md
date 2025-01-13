# Requirements
## Required Software
Terraform v1.2 or newer.

## Optional Software
FastAPI, for testing of API.
Python 3.5 or newer, for local testing of scripts. If using Python for local testing, be sure to run `pip install -r requirements.txt` to install the development dependencies.

## Additional Requirements
You will need an AWS account and to have configured Terraform with your AWS credentials. (e.g. follow https://developer.hashicorp.com/terraform/tutorials/aws-get-started/aws-build)

# How to Run
Execute `terraform plan && terraform apply` in a bash-like prompt. You can use PowerShell on Windows or Terminal on Unix/MacOS.

This will create all necessary resources in AWS, where all of the code in this demo runs.
To view the dashboard of metrics, go to https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#dashboards/dashboard/EnergyMetricsDashboard, or if you are in a different region from `us-west-2` https://my-region.console.aws.amazon.com/cloudwatch/home?region=my-region#dashboards/dashboard/EnergyMetricsDashboard.

To view the API code, navigate to ./source/api.py. This is a demonstration of a web API implemented using FastAPI.

## Configuration
You can configure e.g. data rate with a variable during terraform plan generation via 
`terraform plan -var="upload_interval_minutes=3"`.
See variables.tf for available variables and their defaults.

# How this works
EventBridge triggers AWS Lambda to kick off `random_energy_sites.py` on a regular interval. This creates a JSON of randomly generated energy data for N different sites. Upon upload of this file to s3, AWS Lambda kicks off `process_upload.py` to process these JSONs into entries in DynamoDB. `process_upload.py` also triggers a separate AWS Lambda of `generate_plots.py`, which puts data into CloudWatch to populate a CloudWatch dashboard to view energy balances by Site.

# Design Choices
## Running data generation script in AWS Lambda.
 Given that most of this project was already in Terraform, I decided to run the data generation script in AWS Lambda as well to simplify testing and handling AWS access keys.

## Using dynamoDB `resource` rather than `client`
Using `boto3`'s DynamoDB `resource` rather than `client` meant I didn't need to handle exponential backoff during retries of batch writes in the `process_upload.py` script.

## Using CloudWatch for visualization
While unconventional, using Cloudwatch as a graphing front-end again simplified testing and handling of local AWS configuration. It also reduces dependencies for this project. The downside of this decision is that the aggregation for metrics generation (which backs the dashboard) runs every time a new file is uploaded to s3, which ultimately doesn't scale well at all. 

An alternative to this design would be to use a URL triggered lambda and some clever redirecting within AWS to trigger the metrics generation script via URL Lambda triggers, then redirect to the populated dashboard.
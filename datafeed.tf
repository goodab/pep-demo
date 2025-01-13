resource "aws_s3_bucket" "datafeed" {
  bucket = var.aws_data_bucket_name
  force_destroy = true
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "archive_file" "generate_data_code" {
  type        = "zip"
  source_file = "./source/random_energy_sites.py"
  output_path = "random_energy_sites.zip"
}

resource "aws_lambda_function" "datafeed_lambda" {
  # If the file is not in the current working directory you will need to include a
  # path.module in the filename.
  filename      = "random_energy_sites.zip"
  function_name = "simulate_live_feed"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "random_energy_sites.lambda_handler"
  timeout       = 60
  source_code_hash = data.archive_file.generate_data_code.output_base64sha256

  runtime = "python3.12"

  environment {
    variables = {
      REGION = var.aws_region
      BUCKET_NAME = var.aws_data_bucket_name
      NUM_SITES = var.num_sites
      MAX_GEN_ENERGY_KWH = var.max_gen_energy_kwh
      MIN_GEN_ENERGY_KWH = var.min_gen_energy_kwh
      MAX_CONSUMED_ENERGY_KWH = var.max_consumed_energy_kwh
      MIN_CONSUMED_ENERGY_KWH = var.min_consumed_energy_kwh
    }
  }
}

# EventBridge Rule to trigger Lambda with a configurable rate
# This will error if value =1 because will require singular minute. Rate expressions suck.
resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  name                = "event_every_${var.upload_interval_minutes}_minutes"
  schedule_expression = "rate(${var.upload_interval_minutes} minutes)"
}

# Permission to allow EventBridge to invoke Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.datafeed_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule.arn
}

# Attach EventBridge rule to Lambda
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.lambda_schedule.name
  target_id = "lambda"
  arn       = aws_lambda_function.datafeed_lambda.arn
}


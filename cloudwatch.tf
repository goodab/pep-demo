data "archive_file" "generate_plots_code" {
  type        = "zip"
  source_file = "./source/generate_plots.py"
  output_path = "generate_plots.zip"
}

# Lambda Function
resource "aws_lambda_function" "generate_metrics" {
  function_name = "generate_metrics"
  runtime       = "python3.12"
  handler       = "generate_plots.lambda_handler"
  role          = aws_iam_role.iam_for_lambda.arn
  filename      = "generate_plots.zip" # Update with the zip file path
  source_code_hash = data.archive_file.generate_plots_code.output_base64sha256
  timeout       = 60

   environment {
    variables = {
      TABLE_NAME = var.table_name
    }
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "energy_dashboard" {
  dashboard_name = "EnergyMetricsDashboard"

  dashboard_body = templatefile(
    "dashboardtemplate.json",
    {
      aws_region = var.aws_region
    }
    )
}
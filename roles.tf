resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json

}

# IAM Policy for Lambda to access DynamoDB and CloudWatch
resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda_dynamodb_cloudwatch_policy"
  role = aws_iam_role.iam_for_lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchWriteItem",
          
        ]
        Resource = [
          aws_dynamodb_table.energy_data.arn,
          "${aws_dynamodb_table.energy_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "arn:aws:s3:::${var.aws_data_bucket_name}/*"
      },
      {
        Effect = "Allow"
        Action = [
            "lambda:InvokeFunction"
        ],
        Resource = aws_lambda_function.generate_metrics.arn
      },
      {
        Effect = "Allow"
        Action = [
           "cloudwatch:PutMetricData"
        ],
        Resource = "*"
      }
    ]
  })
}
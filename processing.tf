data "archive_file" "process_upload_code" {
  type        = "zip"
  source_file = "./source/process_upload.py"
  output_path = "process_upload.zip"
}

resource "aws_lambda_function" "processing_lambda" {
  # If the file is not in the current working directory you will need to include a
  # path.module in the filename.
  filename      = "process_upload.zip"
  function_name = "process_upload"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "process_upload.lambda_handler"
  timeout       = 60
  source_code_hash = data.archive_file.process_upload_code.output_base64sha256

  runtime = "python3.12"

  environment {
    variables = {
      REGION = var.aws_region
      TABLE_NAME = var.table_name
    }
  }
}

# Permission for S3 to invoke Lambda
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3InvokeLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.processing_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.datafeed.arn
}

# S3 Bucket Notification
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.datafeed.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.processing_lambda.arn
    events              = ["s3:ObjectCreated:*"] # Trigger on file upload
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
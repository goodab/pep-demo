resource "aws_dynamodb_table" "energy_data" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST" # Use on-demand billing mode for simplicity

  # Define primary key
  hash_key = "site_id"     # Partition key
  range_key = "timestamp"  # Sort key

  # Define attributes
  attribute {
    name = "site_id"
    type = "S" # String
  }

  attribute {
    name = "timestamp"
    type = "S" # String
  }

  # Tags for identification
  tags = {
    Environment = "production"
    Project     = "pep-demo"
  }
}

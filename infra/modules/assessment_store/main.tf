resource "aws_dynamodb_table" "assessments" {
  name         = "${var.project_name}-assessments-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "assessment_id"

  attribute {
    name = "assessment_id"
    type = "S"
  }

  attribute {
    name = "review_status"
    type = "S"
  }

  global_secondary_index {
    name            = "review_status-index"
    hash_key        = "review_status"
    projection_type = "ALL"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "assessment-storage"
  }
}

output "table_name" {
  description = "Name of the assessments DynamoDB table."
  value       = aws_dynamodb_table.assessments.name
}

output "table_arn" {
  description = "ARN of the assessments DynamoDB table."
  value       = aws_dynamodb_table.assessments.arn
}

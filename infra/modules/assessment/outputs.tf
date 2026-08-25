output "lambda_arn" {
  description = "ARN of the assessment Lambda function."
  value       = aws_lambda_function.assessment.arn
}

output "lambda_name" {
  description = "Name of the assessment Lambda function."
  value       = aws_lambda_function.assessment.function_name
}

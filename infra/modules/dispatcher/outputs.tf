output "lambda_arn" {
  description = "ARN of the dispatcher Lambda function."
  value       = aws_lambda_function.dispatcher.arn
}

output "lambda_name" {
  description = "Name of the dispatcher Lambda function."
  value       = aws_lambda_function.dispatcher.function_name
}

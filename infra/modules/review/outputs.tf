output "lambda_arn" {
  description = "ARN of the Lambda creating human review requests."
  value       = aws_lambda_function.review.arn
}

output "decision_lambda_arn" {
  description = "ARN of the Lambda handling human review decisions."
  value       = aws_lambda_function.review_decision.arn
}

output "decision_lambda_name" {
  description = "Name of the Lambda handling human review decisions."
  value       = aws_lambda_function.review_decision.function_name
}

output "list_lambda_arn" {
  description = "ARN of the Lambda listing human reviews."
  value       = aws_lambda_function.review_list.arn
}

output "list_lambda_name" {
  description = "Name of the Lambda listing human reviews."
  value       = aws_lambda_function.review_list.function_name
}

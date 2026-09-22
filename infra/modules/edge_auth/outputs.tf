output "qualified_arn" {
  description = "ARN of the published Lambda@Edge version."
  value       = aws_lambda_function.edge_auth.qualified_arn
}

output "lambda_arn" {
  description = "ARN of the Lambda@Edge function."
  value       = aws_lambda_function.edge_auth.arn
}

output "version" {
  description = "Published Lambda@Edge version."
  value       = aws_lambda_function.edge_auth.version
}

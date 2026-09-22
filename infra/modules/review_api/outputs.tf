output "api_endpoint" {
  description = "Base URL of the human review API."
  value       = aws_apigatewayv2_api.review.api_endpoint
}

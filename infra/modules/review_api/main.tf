resource "aws_apigatewayv2_api" "review" {
  name          = "${var.project_name}-review-api-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = [
      "http://localhost:8080",
      "https://d3i9c4r4p4ftam.cloudfront.net",
      "https://responsible-gaming.manuworld.fr",
    ]

    allow_methods = [
      "GET",
      "POST",
      "OPTIONS",
    ]

    allow_headers = [
      "Content-Type",
      "Authorization",
    ]

    max_age = 300
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id = aws_apigatewayv2_api.review.id

  name             = "${var.project_name}-cognito-${var.environment}"
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]

  jwt_configuration {
    audience = [
      var.cognito_user_pool_client_id,
    ]

    issuer = "https://${var.cognito_user_pool_endpoint}"
  }
}

resource "aws_apigatewayv2_integration" "review_decision" {
  api_id = aws_apigatewayv2_api.review.id

  integration_type   = "AWS_PROXY"
  integration_uri    = var.decision_lambda_arn
  integration_method = "POST"

  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "review_list" {
  api_id = aws_apigatewayv2_api.review.id

  integration_type   = "AWS_PROXY"
  integration_uri    = var.list_lambda_arn
  integration_method = "POST"

  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "review_decision" {
  api_id = aws_apigatewayv2_api.review.id

  route_key = "POST /assessments/{assessment_id}/review"
  target    = "integrations/${aws_apigatewayv2_integration.review_decision.id}"

  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "review_list" {
  api_id = aws_apigatewayv2_api.review.id

  route_key = "GET /assessments"
  target    = "integrations/${aws_apigatewayv2_integration.review_list.id}"

  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "review_detail" {
  api_id = aws_apigatewayv2_api.review.id

  route_key = "GET /assessments/{assessment_id}"
  target    = "integrations/${aws_apigatewayv2_integration.review_list.id}"

  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.review.id

  name        = "$default"
  auto_deploy = true

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.decision_lambda_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.review.execution_arn}/*/POST/assessments/*/review"
}

resource "aws_lambda_permission" "allow_api_gateway_review_list" {
  statement_id  = "AllowExecutionFromAPIGatewayReviewList"
  action        = "lambda:InvokeFunction"
  function_name = var.list_lambda_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.review.execution_arn}/*/GET/assessments*"
}

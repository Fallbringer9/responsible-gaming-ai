variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "decision_lambda_arn" {
  description = "ARN of the Lambda handling human review decisions."
  type        = string
}

variable "decision_lambda_name" {
  description = "Name of the Lambda handling human review decisions."
  type        = string
}

variable "list_lambda_arn" {
  description = "ARN of the Lambda listing human reviews."
  type        = string
}

variable "list_lambda_name" {
  description = "Name of the Lambda listing human reviews."
  type        = string
}

variable "cognito_user_pool_client_id" {
  description = "Cognito app client ID accepted by the API JWT authorizer."
  type        = string
}

variable "cognito_user_pool_endpoint" {
  description = "OIDC issuer endpoint of the Cognito user pool."
  type        = string
}

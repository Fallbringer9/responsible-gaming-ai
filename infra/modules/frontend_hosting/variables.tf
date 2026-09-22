variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "domain_name" {
  description = "Custom domain name used by the frontend."
  type        = string
}

variable "certificate_arn" {
  description = "ARN of the ACM certificate used by CloudFront."
  type        = string
}

variable "edge_auth_lambda_arn" {
  description = "Qualified ARN of the Lambda@Edge authentication function."
  type        = string
}

variable "api_domain_name" {
  description = "API Gateway domain name used as the CloudFront API origin."
  type        = string
}

variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "lambda_package_path" {
  description = "Path to the Lambda@Edge deployment package."
  type        = string
}

variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "assessment_table_name" {
  description = "Name of the DynamoDB table storing assessments."
  type        = string
}

variable "assessment_table_arn" {
  description = "ARN of the DynamoDB table storing assessments."
  type        = string
}

variable "lambda_package_path" {
  description = "Path to the deployment package for the review Lambda."
  type        = string
}

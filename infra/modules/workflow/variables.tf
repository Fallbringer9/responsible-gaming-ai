variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "assessment_lambda_arn" {
  description = "ARN of the Lambda executing the responsible gaming assessment."
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

variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "input_bucket_arn" {
  description = "ARN of the S3 bucket containing player activity snapshots."
  type        = string
}

variable "knowledge_base_id" {
  description = "Amazon Bedrock Knowledge Base identifier."
  type        = string
}

variable "knowledge_base_arn" {
  description = "ARN of the Amazon Bedrock Knowledge Base."
  type        = string
}

variable "model_id" {
  description = "Bedrock inference profile or model identifier."
  type        = string
}

variable "lambda_package_path" {
  description = "Path to the assessment Lambda deployment package."
  type        = string
}

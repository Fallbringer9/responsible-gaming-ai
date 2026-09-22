variable "aws_region" {
  description = "AWS region used to deploy the infrastructure."
  type        = string
}

variable "aws_profile" {
  description = "Local AWS CLI profile used by Terraform."
  type        = string
}

variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "knowledge_base_id" {
  description = "Bedrock Knowledge Base identifier."
  type        = string
}

variable "knowledge_base_arn" {
  description = "Bedrock Knowledge Base ARN."
  type        = string
}

variable "model_id" {
  description = "Bedrock inference profile or model identifier."
  type        = string
}

variable "frontend_domain_name" {
  description = "Custom domain name used by the Responsible Gaming frontend."
  type        = string
  default     = "responsible-gaming.manuworld.fr"
}

variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "source_bucket_arn" {
  description = "ARN of the S3 bucket allowed to send messages to the analysis queue."
  type        = string
}

variable "max_receive_count" {
  description = "Number of processing attempts before moving a message to the DLQ."
  type        = number
  default     = 3
}

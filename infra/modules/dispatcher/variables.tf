variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment."
  type        = string
}

variable "queue_arn" {
  description = "ARN of the SQS queue consumed by the dispatcher."
  type        = string
}

variable "state_machine_arn" {
  description = "ARN of the Step Functions state machine started by the dispatcher."
  type        = string
}

variable "lambda_package_path" {
  description = "Path to the deployment package containing the dispatcher Lambda code."
  type        = string
}

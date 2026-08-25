output "input_bucket_name" {
  description = "Name of the player activity input bucket."
  value       = module.storage.bucket_name
}

output "input_bucket_arn" {
  description = "ARN of the player activity input bucket."
  value       = module.storage.bucket_arn
}

output "analysis_queue_url" {
  description = "URL of the analysis queue."
  value       = module.queue.queue_url
}

output "analysis_queue_arn" {
  description = "ARN of the analysis queue."
  value       = module.queue.queue_arn
}

output "analysis_dlq_url" {
  description = "URL of the analysis dead-letter queue."
  value       = module.queue.dlq_url
}

output "risk_assessment_state_machine_arn" {
  description = "ARN of the risk assessment Step Functions state machine."
  value       = module.workflow.state_machine_arn
}

output "dispatcher_lambda_arn" {
  description = "ARN of the dispatcher Lambda function."
  value       = module.dispatcher.lambda_arn
}

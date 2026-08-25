output "queue_url" {
  description = "URL of the analysis queue."
  value       = aws_sqs_queue.analysis.url
}

output "queue_arn" {
  description = "ARN of the analysis queue."
  value       = aws_sqs_queue.analysis.arn
}

output "dlq_url" {
  description = "URL of the dead-letter queue."
  value       = aws_sqs_queue.dlq.url
}

output "dlq_arn" {
  description = "ARN of the dead-letter queue."
  value       = aws_sqs_queue.dlq.arn
}

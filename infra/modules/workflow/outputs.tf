output "state_machine_arn" {
  description = "ARN of the risk assessment Step Functions state machine."
  value       = aws_sfn_state_machine.risk_assessment.arn
}

output "state_machine_name" {
  description = "Name of the risk assessment Step Functions state machine."
  value       = aws_sfn_state_machine.risk_assessment.name
}

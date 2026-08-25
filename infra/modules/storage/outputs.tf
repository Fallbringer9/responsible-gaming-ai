output "bucket_name" {
  description = "Name of the player activity input bucket."
  value       = aws_s3_bucket.input.bucket
}

output "bucket_arn" {
  description = "ARN of the player activity input bucket."
  value       = aws_s3_bucket.input.arn
}

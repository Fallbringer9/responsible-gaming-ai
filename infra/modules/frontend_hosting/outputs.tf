output "bucket_name" {
  description = "Name of the private frontend S3 bucket."
  value       = aws_s3_bucket.frontend.bucket
}

output "cloudfront_distribution_id" {
  description = "ID of the frontend CloudFront distribution."
  value       = aws_cloudfront_distribution.frontend.id
}

output "cloudfront_domain_name" {
  description = "CloudFront domain serving the frontend."
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "cloudfront_hosted_zone_id" {
  description = "Route 53 hosted zone ID used by CloudFront."
  value       = aws_cloudfront_distribution.frontend.hosted_zone_id
}

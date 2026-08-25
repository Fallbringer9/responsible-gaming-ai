resource "aws_sqs_queue" "dlq" {
  name = "${var.project_name}-analysis-dlq-${var.environment}"

  message_retention_seconds = 1209600

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "analysis-dead-letter"
  }
}

resource "aws_sqs_queue" "analysis" {
  name = "${var.project_name}-analysis-${var.environment}"

  visibility_timeout_seconds = 180

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.max_receive_count
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "analysis-queue"
  }
}

resource "aws_sqs_queue_policy" "allow_s3" {
  queue_url = aws_sqs_queue.analysis.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "AllowS3ToSendMessages"
        Effect = "Allow"

        Principal = {
          Service = "s3.amazonaws.com"
        }

        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.analysis.arn

        Condition = {
          ArnEquals = {
            "aws:SourceArn" = var.source_bucket_arn
          }
        }
      }
    ]
  })
}

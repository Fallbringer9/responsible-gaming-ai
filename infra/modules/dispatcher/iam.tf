resource "aws_iam_role" "dispatcher" {
  name = "${var.project_name}-dispatcher-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "lambda.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}


resource "aws_iam_role_policy" "dispatcher" {
  name = "${var.project_name}-dispatcher-policy-${var.environment}"
  role = aws_iam_role.dispatcher.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ConsumeAnalysisQueue"
        Effect = "Allow"

        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]

        Resource = var.queue_arn
      },
      {
        Sid    = "StartRiskAssessmentWorkflow"
        Effect = "Allow"

        Action = [
          "states:StartExecution"
        ]

        Resource = var.state_machine_arn
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "basic_execution" {
  role = aws_iam_role.dispatcher.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

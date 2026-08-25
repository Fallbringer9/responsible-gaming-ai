resource "aws_iam_role" "step_functions" {
  name = "${var.project_name}-workflow-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "states.amazonaws.com"
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

resource "aws_iam_role_policy" "invoke_assessment" {
  name = "${var.project_name}-workflow-invoke-assessment-${var.environment}"
  role = aws_iam_role.step_functions.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "lambda:InvokeFunction"
        ]

        Resource = var.assessment_lambda_arn
      }
    ]
  })
}

resource "aws_iam_role_policy" "write_assessment" {
  name = "${var.project_name}-workflow-write-assessment-${var.environment}"
  role = aws_iam_role.step_functions.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "dynamodb:PutItem"
        ]

        Resource = var.assessment_table_arn
      }
    ]
  })
}

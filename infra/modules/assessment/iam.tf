resource "aws_iam_role" "assessment" {
  name = "${var.project_name}-assessment-${var.environment}"

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


resource "aws_iam_role_policy" "assessment" {
  name = "${var.project_name}-assessment-policy-${var.environment}"
  role = aws_iam_role.assessment.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "ReadPlayerSnapshots"
        Effect = "Allow"

        Action = [
          "s3:GetObject"
        ]

        Resource = "${var.input_bucket_arn}/*"
      },

      {
        Sid    = "RetrieveResponsibleGamingKnowledge"
        Effect = "Allow"

        Action = [
          "bedrock:Retrieve"
        ]

        Resource = var.knowledge_base_arn
      },

      {
        Sid    = "InvokeBedrockModel"
        Effect = "Allow"

        Action = [
          "bedrock:InvokeModel"
        ]

        Resource = "*"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "basic_execution" {
  role = aws_iam_role.assessment.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

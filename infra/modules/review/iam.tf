resource "aws_iam_role" "review_lambda" {
  name = "${var.project_name}-review-lambda-${var.environment}"

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

resource "aws_iam_role_policy_attachment" "review_lambda_basic_execution" {
  role       = aws_iam_role.review_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "review_dynamodb" {
  name = "${var.project_name}-review-dynamodb-${var.environment}"
  role = aws_iam_role.review_lambda.id

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

resource "aws_iam_role" "review_decision_lambda" {
  name = "${var.project_name}-review-decision-lambda-${var.environment}"

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

resource "aws_iam_role_policy_attachment" "review_decision_basic_execution" {
  role       = aws_iam_role.review_decision_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "review_decision" {
  name = "${var.project_name}-review-decision-${var.environment}"
  role = aws_iam_role.review_decision_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "dynamodb:GetItem",
          "dynamodb:UpdateItem"
        ]

        Resource = var.assessment_table_arn
      },
      {
        Effect = "Allow"

        Action = [
          "states:SendTaskSuccess"
        ]

        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "review_list_lambda" {
  name = "${var.project_name}-review-list-lambda-${var.environment}"

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


resource "aws_iam_role_policy_attachment" "review_list_basic_execution" {
  role       = aws_iam_role.review_list_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


resource "aws_iam_role_policy" "review_list_dynamodb" {
  name = "${var.project_name}-review-list-dynamodb-${var.environment}"
  role = aws_iam_role.review_list_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "dynamodb:Query"
        ]

        Resource = [
          "${var.assessment_table_arn}/index/review_status-index"
        ]
      },
      {
        Effect = "Allow"

        Action = [
          "dynamodb:GetItem"
        ]

        Resource = [
          var.assessment_table_arn
        ]
      }
    ]
  })
}

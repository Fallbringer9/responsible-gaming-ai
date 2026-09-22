terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type = "Service"

      identifiers = [
        "lambda.amazonaws.com",
        "edgelambda.amazonaws.com",
      ]
    }
  }
}

resource "aws_iam_role" "edge_auth" {
  name = "${var.project_name}-edge-auth-${var.environment}"

  assume_role_policy = data.aws_iam_policy_document.assume_role.json

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "cloudfront-authentication"
  }
}

resource "aws_iam_role_policy_attachment" "basic_execution" {
  role = aws_iam_role.edge_auth.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "edge_auth" {
  function_name = "${var.project_name}-edge-auth-${var.environment}"

  role = aws_iam_role.edge_auth.arn

  runtime       = "nodejs22.x"
  architectures = ["x86_64"]

  handler = "index.handler"

  filename         = var.lambda_package_path
  source_code_hash = filebase64sha256(var.lambda_package_path)

  publish = true

  timeout     = 5
  memory_size = 128

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "cloudfront-authentication"
  }
}

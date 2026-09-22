resource "aws_lambda_function" "review" {
  function_name = "${var.project_name}-review-${var.environment}"

  role = aws_iam_role.review_lambda.arn

  runtime       = "python3.13"
  architectures = ["arm64"]

  handler = "responsible_gaming.interfaces.lambda_handlers.review.handler"

  filename         = var.lambda_package_path
  source_code_hash = filebase64sha256(var.lambda_package_path)

  timeout     = 30
  memory_size = 256

  environment {
    variables = {
      ASSESSMENT_TABLE_NAME = var.assessment_table_name
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_lambda_function" "review_decision" {
  function_name = "${var.project_name}-review-decision-${var.environment}"

  role = aws_iam_role.review_decision_lambda.arn

  runtime       = "python3.13"
  architectures = ["arm64"]

  handler = "responsible_gaming.interfaces.lambda_handlers.review_decision.handler"

  filename         = var.lambda_package_path
  source_code_hash = filebase64sha256(var.lambda_package_path)

  timeout     = 30
  memory_size = 256

  environment {
    variables = {
      ASSESSMENT_TABLE_NAME = var.assessment_table_name
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_lambda_function" "review_list" {
  function_name = "${var.project_name}-review-list-${var.environment}"

  role = aws_iam_role.review_list_lambda.arn

  runtime       = "python3.13"
  architectures = ["arm64"]

  handler = "responsible_gaming.interfaces.lambda_handlers.review_list.handler"

  filename         = var.lambda_package_path
  source_code_hash = filebase64sha256(var.lambda_package_path)

  timeout     = 30
  memory_size = 256

  environment {
    variables = {
      ASSESSMENT_TABLE_NAME = var.assessment_table_name
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_lambda_function" "assessment" {
  function_name = "${var.project_name}-assessment-${var.environment}"

  role = aws_iam_role.assessment.arn

  runtime = "python3.13"

  architectures = ["arm64"]

  handler = (
    "responsible_gaming.interfaces.lambda_handlers.assessment.handler"
  )

  filename = var.lambda_package_path

  source_code_hash = filebase64sha256(
    var.lambda_package_path
  )

  timeout     = 120
  memory_size = 512

  environment {
    variables = {
      KNOWLEDGE_BASE_ID = var.knowledge_base_id
      MODEL_ID          = var.model_id
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "risk-assessment"
  }
}

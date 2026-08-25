resource "aws_lambda_function" "dispatcher" {
  function_name = "${var.project_name}-dispatcher-${var.environment}"

  role = aws_iam_role.dispatcher.arn

  runtime = "python3.13"

  handler = (
    "responsible_gaming.interfaces.lambda_handlers.dispatcher.handler"
  )

  filename = var.lambda_package_path

  source_code_hash = filebase64sha256(
    var.lambda_package_path
  )

  timeout     = 30
  memory_size = 256

  environment {
    variables = {
      STATE_MACHINE_ARN = var.state_machine_arn
    }
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "workflow-dispatcher"
  }
}


resource "aws_lambda_event_source_mapping" "analysis_queue" {
  event_source_arn = var.queue_arn
  function_name    = aws_lambda_function.dispatcher.arn

  batch_size = 10

  function_response_types = [
    "ReportBatchItemFailures"
  ]

  scaling_config {
    maximum_concurrency = 10
  }
}

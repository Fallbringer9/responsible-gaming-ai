module "storage" {
  source = "../../modules/storage"

  project_name = var.project_name
  environment  = var.environment
}

module "queue" {
  source = "../../modules/queue"

  project_name      = var.project_name
  environment       = var.environment
  source_bucket_arn = module.storage.bucket_arn
}

resource "aws_s3_bucket_notification" "input_to_analysis_queue" {
  bucket = module.storage.bucket_name

  queue {
    queue_arn = module.queue.queue_arn
    events    = ["s3:ObjectCreated:*"]
  }

  depends_on = [
    module.queue,
  ]
}

module "assessment" {
  source = "../../modules/assessment"

  project_name = var.project_name
  environment  = var.environment

  input_bucket_arn = module.storage.bucket_arn

  knowledge_base_id  = var.knowledge_base_id
  knowledge_base_arn = var.knowledge_base_arn
  model_id           = var.model_id

  lambda_package_path = "${path.module}/../../../dist/assessment.zip"
}

module "workflow" {
  source = "../../modules/workflow"

  project_name = var.project_name
  environment  = var.environment

  assessment_lambda_arn = module.assessment.lambda_arn

  assessment_table_name = module.assessment_store.table_name
  assessment_table_arn  = module.assessment_store.table_arn
}

module "dispatcher" {
  source = "../../modules/dispatcher"

  project_name      = var.project_name
  environment       = var.environment
  queue_arn         = module.queue.queue_arn
  state_machine_arn = module.workflow.state_machine_arn

  lambda_package_path = "${path.module}/../../../dist/dispatcher.zip"
}

module "assessment_store" {
  source = "../../modules/assessment_store"

  project_name = var.project_name
  environment  = var.environment
}

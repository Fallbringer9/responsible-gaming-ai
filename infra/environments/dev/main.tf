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

  review_lambda_arn = module.review.lambda_arn
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

module "review" {
  source = "../../modules/review"

  project_name = var.project_name
  environment  = var.environment

  assessment_table_name = module.assessment_store.table_name
  assessment_table_arn  = module.assessment_store.table_arn

  lambda_package_path = "${path.module}/../../../dist/review.zip"
}

module "review_api" {
  source = "../../modules/review_api"

  project_name = var.project_name
  environment  = var.environment

  decision_lambda_arn  = module.review.decision_lambda_arn
  decision_lambda_name = module.review.decision_lambda_name

  list_lambda_arn  = module.review.list_lambda_arn
  list_lambda_name = module.review.list_lambda_name

  cognito_user_pool_client_id = aws_cognito_user_pool_client.operator_frontend.id
  cognito_user_pool_endpoint  = aws_cognito_user_pool.operator.endpoint
}

resource "aws_acm_certificate" "frontend" {
  provider = aws.us_east_1

  domain_name       = "responsible-gaming.manuworld.fr"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_route53_record" "frontend_certificate_validation" {
  for_each = {
    for option in aws_acm_certificate.frontend.domain_validation_options :
    option.domain_name => {
      name   = option.resource_record_name
      record = option.resource_record_value
      type   = option.resource_record_type
    }
  }

  zone_id = "Z0118305PU93W8XK8MQU"

  name    = each.value.name
  type    = each.value.type
  records = [each.value.record]

  ttl = 60
}

resource "aws_acm_certificate_validation" "frontend" {
  provider = aws.us_east_1

  certificate_arn = aws_acm_certificate.frontend.arn

  validation_record_fqdns = [
    for record in aws_route53_record.frontend_certificate_validation :
    record.fqdn
  ]
}

module "frontend_hosting" {
  source = "../../modules/frontend_hosting"

  project_name = var.project_name
  environment  = var.environment

  domain_name          = "responsible-gaming.manuworld.fr"
  certificate_arn      = aws_acm_certificate_validation.frontend.certificate_arn
  edge_auth_lambda_arn = module.edge_auth.qualified_arn

  api_domain_name = trimprefix(
    module.review_api.api_endpoint,
    "https://"
  )
}

resource "aws_route53_record" "frontend" {
  zone_id = "Z0118305PU93W8XK8MQU"

  name = "responsible-gaming.manuworld.fr"
  type = "A"

  alias {
    name                   = module.frontend_hosting.cloudfront_domain_name
    zone_id                = module.frontend_hosting.cloudfront_hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_cognito_user_pool" "operator" {
  name = "${var.project_name}-operator-${var.environment}"

  username_attributes = [
    "email",
  ]

  auto_verified_attributes = [
    "email",
  ]

  password_policy {
    minimum_length                   = 12
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 7
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "operator-authentication"
  }
}

resource "aws_cognito_user_pool_client" "operator_frontend" {
  name         = "${var.project_name}-frontend-${var.environment}"
  user_pool_id = aws_cognito_user_pool.operator.id

  generate_secret = false

  allowed_oauth_flows_user_pool_client = true

  allowed_oauth_flows = [
    "code",
  ]

  allowed_oauth_scopes = [
    "openid",
    "email",
    "profile",
  ]

  callback_urls = [
    "https://${var.frontend_domain_name}/auth/callback",
  ]

  logout_urls = [
    "https://${var.frontend_domain_name}/",
  ]

  supported_identity_providers = [
    "COGNITO",
  ]

  prevent_user_existence_errors = "ENABLED"
}

resource "aws_cognito_user_pool_domain" "operator" {
  domain                = "responsible-gaming-operator-dev"
  user_pool_id          = aws_cognito_user_pool.operator.id
  managed_login_version = 2
}

module "edge_auth" {
  source = "../../modules/edge_auth"

  providers = {
    aws = aws.us_east_1
  }

  project_name = var.project_name
  environment  = var.environment

  lambda_package_path = "${path.module}/../../../dist/edge-auth.zip"
}

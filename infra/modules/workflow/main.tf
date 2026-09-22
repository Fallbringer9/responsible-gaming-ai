resource "aws_sfn_state_machine" "risk_assessment" {
  name     = "${var.project_name}-risk-assessment-${var.environment}"
  role_arn = aws_iam_role.step_functions.arn

  definition = jsonencode({
    Comment       = "Responsible gaming risk assessment workflow"
    QueryLanguage = "JSONata"

    StartAt = "RunAssessment"

    States = {
      RunAssessment = {
        Type     = "Task"
        Resource = "arn:aws:states:::lambda:invoke"

        Arguments = {
          FunctionName = var.assessment_lambda_arn
          Payload      = "{% $states.input %}"
        }

        Output = "{% $states.result.Payload %}"

        Next = "NeedHumanReview"
      }

      NeedHumanReview = {
        Type = "Choice"

        Choices = [
          {
            Condition = "{% $states.input.human_review_required = true %}"
            Next      = "WaitForHumanReview"
          }
        ]

        Default = "Finalize"
      }

      WaitForHumanReview = {
        Type     = "Task"
        Resource = "arn:aws:states:::lambda:invoke.waitForTaskToken"

        Arguments = {
          FunctionName = var.review_lambda_arn

          Payload = {
            assessment_id = "{% $states.input.assessment_id %}"
            assessment    = "{% $states.input.assessment %}"
            task_token    = "{% $states.context.Task.Token %}"
          }
        }

        Next = "Finalize"
      }

      Finalize = {
        Type     = "Task"
        Resource = "arn:aws:states:::dynamodb:updateItem"

        Arguments = {
          TableName = var.assessment_table_name

          Key = {
            assessment_id = {
              S = "{% $states.input.assessment_id %}"
            }
          }

          UpdateExpression = "SET assessment = :assessment, human_review_required = :human_review_required REMOVE task_token"

          ExpressionAttributeValues = {
            ":assessment" = {
              S = "{% $string($states.input.assessment) %}"
            }

            ":human_review_required" = {
              BOOL = "{% $states.input.human_review_required %}"
            }
          }
        }

        End = true
      }
    }
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

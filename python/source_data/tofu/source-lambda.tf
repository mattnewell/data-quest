data "archive_file" "source_data" {
  type = "zip"

  source_file = "${path.module}/../source_data.py"
  output_path = "${path.module}/source_data.zip"
}

resource "aws_s3_object" "source_data" {
  bucket = var.s3_bucket
  key    = "source_data.zip"
  source = data.archive_file.source_data.output_path
  etag   = filemd5(data.archive_file.source_data.output_path)
}

resource "aws_lambda_function" "source_data" {
  function_name = "newell-source-data"
  timeout       = 30 # seconds
  image_uri     = "275279264324.dkr.ecr.us-east-1.amazonaws.com/newell-source-data:latest"
  package_type  = "Image"

  role = aws_iam_role.source_data.arn

#  environment {
#    variables = {
#      ENVIRONMENT = var.env_name
#    }
#  }
}

resource "aws_cloudwatch_log_group" "source_data" {
  name = "/aws/lambda/${aws_lambda_function.source_data.function_name}"

  retention_in_days = 5
}

resource "aws_iam_role" "source_data" {
  name = "newell_lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "source_data" {
  for_each = toset([
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  ])

  role       = aws_iam_role.source_data.name
  policy_arn = each.value
}


resource "aws_cloudwatch_event_rule" "source_data" {
    name = "newell-source-data-schedule"
    schedule_expression = "cron(0 0 ? * 1 *)" # every sunday at 00:00 UTC
}

resource "aws_cloudwatch_event_target" "source_data" {
    rule = aws_cloudwatch_event_rule.source_data.name
    target_id = "processing_lambda"
    arn = aws_lambda_function.source_data.arn
}

resource "aws_lambda_permission" "source_data" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.source_data.function_name
    principal = "events.amazonaws.com"
}
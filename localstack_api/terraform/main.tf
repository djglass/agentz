
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  endpoints {
    s3         = "http://localhost:4566"
    lambda     = "http://localhost:4566"
    apigateway = "http://localhost:4566"
  }
}

#resource "aws_s3_bucket" "demo_bucket" {
#  bucket = "my-local-bucket"
#
#  lifecycle {
#    prevent_destroy = false
#    ignore_changes  = all
#  }
#}

resource "aws_lambda_function" "demo_lambda" {
  function_name = "demo-function"
  filename      = "../lambda/lambda_function_payload.zip"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  role          = "arn:aws:iam::000000000000:role/lambda-role"
  timeout       = 300
  source_code_hash = filebase64sha256("../lambda/lambda_function_payload.zip")
}


resource "aws_api_gateway_rest_api" "demo_api" {
  name = "demo-api"
}

resource "aws_api_gateway_resource" "hello" {
  rest_api_id = aws_api_gateway_rest_api.demo_api.id
  parent_id   = aws_api_gateway_rest_api.demo_api.root_resource_id
  path_part   = "hello"
}

resource "aws_api_gateway_method" "get_hello" {
  rest_api_id   = aws_api_gateway_rest_api.demo_api.id
  resource_id   = aws_api_gateway_resource.hello.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_get" {
  rest_api_id             = aws_api_gateway_rest_api.demo_api.id
  resource_id             = aws_api_gateway_resource.hello.id
  http_method             = aws_api_gateway_method.get_hello.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.demo_lambda.invoke_arn
}

resource "aws_api_gateway_method" "post_hello" {
  rest_api_id   = aws_api_gateway_rest_api.demo_api.id
  resource_id   = aws_api_gateway_resource.hello.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_post" {
  rest_api_id             = aws_api_gateway_rest_api.demo_api.id
  resource_id             = aws_api_gateway_resource.hello.id
  http_method             = aws_api_gateway_method.post_hello.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.demo_lambda.invoke_arn
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.demo_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.demo_api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "demo_deployment" {
  depends_on  = [aws_api_gateway_integration.lambda_get, aws_api_gateway_integration.lambda_post]
  rest_api_id = aws_api_gateway_rest_api.demo_api.id
  stage_name = "v1"
  description = "Full redeploy ${timestamp()}"
}



terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  profile = "default"
}

# Create Roles
resource "aws_iam_role" "lambda_role" {
  name = "BudgetBoyLambdaRole"
  description = "Allows Lambda functions access to SQS Queues, EventBridge, and RDS"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
  }
  EOF
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonSQSFullAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole",
    "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess"
  ]
}

resource "aws_iam_role" "apigw_role" {
  name = "BudgetBoyAPIGatewayRole"
  description = "Allows API Gateway to push logs to CloudWatch Logs and Send messages to SQS Queues"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": "apigateway.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
  }
  EOF
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonSQSFullAccess",
    "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
  ]
}

resource "aws_iam_role" "eventbridge_role" {
  name = "BB-EventBridgeRuleRole"
  assume_role_policy = <<EOF
  {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "events.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
  }
  EOF
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonSQSFullAccess"
  ]
}

# Create Zip files for lambdas FYI: ${path.module} means current directory
data "archive_file" "clear_budget_zip" {
    type = "zip"
    source_dir = "${path.module}/LambdaCodeFiles/BB-Clear-Budget-Lambda"
    output_path = "${path.module}/LambdaCodeFiles/TFzips/BB-Clear-Budget-Lambda.zip"
}
data "archive_file" "create_budget_zip" {
    type = "zip"
    source_dir = "${path.module}/LambdaCodeFiles/BB-Create-Budget-Lambda"
    output_path = "${path.module}/LambdaCodeFiles/TFzips/BB-Create-Budget-Lambda.zip"
}
data "archive_file" "delete_budget_zip" {
    type = "zip"
    source_dir = "${path.module}/LambdaCodeFiles/BB-Delete-Budget-Lambda"
    output_path = "${path.module}/LambdaCodeFiles/TFzips/BB-Delete-Budget-Lambda.zip"
}
data "archive_file" "get_budget_zip" {
    type = "zip"
    source_dir = "${path.module}/LambdaCodeFiles/BB-Get-Budgets-Lambda"
    output_path = "${path.module}/LambdaCodeFiles/TFzips/BB-Get-Budgets-Lambda.zip"
}
data "archive_file" "get_categories_zip" {
    type = "zip"
    source_dir = "${path.module}/LambdaCodeFiles/BB-Get-Categories-Lambda"
    output_path = "${path.module}/LambdaCodeFiles/TFzips/BB-Get-Categories-Lambda.zip"
}
data "archive_file" "get_reportdata_zip" {
    type = "zip"
    source_dir = "${path.module}/LambdaCodeFiles/BB-Get-ReportData-Lambda"
    output_path = "${path.module}/LambdaCodeFiles/TFzips/BB-Get-ReportData-Lambda.zip"
}
data "archive_file" "get_userswithaccess_zip" {
    type = "zip"
    source_dir = "${path.module}/LambdaCodeFiles/BB-Get-UsersWithAccess-Lambda"
    output_path = "${path.module}/LambdaCodeFiles/TFzips/BB-Get-UsersWithAccess-Lambda.zip"
}
data "archive_file" "share_budget_zip" {
    type = "zip"
    source_dir = "${path.module}/LambdaCodeFiles/BB-Share-Budget-Lambda"
    output_path = "${path.module}/LambdaCodeFiles/TFzips/BB-Share-Budget-Lambda.zip"
}
data "archive_file" "update_budget_zip" {
    type = "zip"
    source_dir = "${path.module}/LambdaCodeFiles/BB-Update-Budget-Lambda"
    output_path = "${path.module}/LambdaCodeFiles/TFzips/BB-Update-Budget-Lambda.zip"
}

# Create Lambda Functions
resource "aws_lambda_function" "clear_budget" {
    filename = "${path.module}/LambdaCodeFiles/TFzips/BB-Clear-Budget-Lambda.zip"
    function_name = "BB-Clear-Budget-Lambda"
    role = aws_iam_role.lambda_role.arn
    handler = "BB-Clear-Budget-Lambda.lambda_handler"
    runtime = "python3.9"
}

resource "aws_lambda_function" "create_budget" {
    filename = "${path.module}/LambdaCodeFiles/TFzips/BB-Create-Budget-Lambda.zip"
    function_name = "BB-Create-Budget-Lambda"
    role = aws_iam_role.lambda_role.arn
    handler = "BB-Create-Budget-Lambda.lambda_handler"
    runtime = "python3.9"
}

resource "aws_lambda_function" "delete_budget" {
    filename = "${path.module}/LambdaCodeFiles/TFzips/BB-Delete-Budget-Lambda.zip"
    function_name = "BB-Delete-Budget-Lambda"
    role = aws_iam_role.lambda_role.arn
    handler = "BB-Delete-Budget-Lambda.lambda_handler"
    runtime = "python3.9"
}

resource "aws_lambda_function" "get_budgets" {
    filename = "${path.module}/LambdaCodeFiles/TFzips/BB-Get-Budgets-Lambda.zip"
    function_name = "BB-Get-Budgets-Lambda"
    role = aws_iam_role.lambda_role.arn
    handler = "BB-Get-Budgets-Lambda.lambda_handler"
    runtime = "python3.9"
}

resource "aws_lambda_function" "get_categories" {
    filename = "${path.module}/LambdaCodeFiles/TFzips/BB-Get-Categories-Lambda.zip"
    function_name = "BB-Get-Categories-Lambda"
    role = aws_iam_role.lambda_role.arn
    handler = "BB-Get-Categories-Lambda.lambda_handler"
    runtime = "python3.9"
}

resource "aws_lambda_function" "get_reportdata" {
    filename = "${path.module}/LambdaCodeFiles/TFzips/BB-Get-ReportData-Lambda.zip"
    function_name = "BB-Get-ReportData-Lambda"
    role = aws_iam_role.lambda_role.arn
    handler = "BB-Get-ReportData-Lambda.lambda_handler"
    runtime = "python3.9"
}

resource "aws_lambda_function" "get_userswithaccess" {
    filename = "${path.module}/LambdaCodeFiles/TFzips/BB-Get-UsersWithAccess-Lambda.zip"
    function_name = "BB-Get-UsersWithAccess-Lambda"
    role = aws_iam_role.lambda_role.arn
    handler = "BB-Get-UsersWithAccess-Lambda.lambda_handler"
    runtime = "python3.9"
}

resource "aws_lambda_function" "share_budget" {
    filename = "${path.module}/LambdaCodeFiles/TFzips/BB-Share-Budget-Lambda.zip"
    function_name = "BB-Share-Budget-Lambda"
    role = aws_iam_role.lambda_role.arn
    handler = "BB-Share-Budget-Lambda.lambda_handler"
    runtime = "python3.9"
}

resource "aws_lambda_function" "update_budget" {
    filename = "${path.module}/LambdaCodeFiles/TFzips/BB-Update-Budget-Lambda.zip"
    function_name = "BB-Update-Budget-Lambda"
    role = aws_iam_role.lambda_role.arn
    handler = "BB-Update-Budget-Lambda.lambda_handler"
    runtime = "python3.9"
}

# Create API Gateway
resource "aws_api_gateway_rest_api" "bb_api" {
  name = "BudgetBoyAPI"
}

# Create API Gateway Resources
resource "aws_api_gateway_resource" "budgets" {
  rest_api_id = aws_api_gateway_rest_api.bb_api.id
  parent_id   = aws_api_gateway_rest_api.bb_api.root_resource_id
  path_part   = "budgets"
}

resource "aws_api_gateway_resource" "budgets_sharing" {
  rest_api_id = aws_api_gateway_rest_api.bb_api.id
  parent_id   = aws_api_gateway_resource.budgets.id
  path_part   = "sharing"
}

resource "aws_api_gateway_resource" "categories" {
  rest_api_id = aws_api_gateway_rest_api.bb_api.id
  parent_id   = aws_api_gateway_rest_api.bb_api.root_resource_id
  path_part   = "categories"
}

resource "aws_api_gateway_resource" "reportdata" {
  rest_api_id = aws_api_gateway_rest_api.bb_api.id
  parent_id   = aws_api_gateway_rest_api.bb_api.root_resource_id
  path_part   = "reportdata"
}

# Create Cognito User Pool
resource "aws_cognito_user_pool" "budget_boy" {
  name = "Budget Boy"
  auto_verified_attributes   = [
      "email",
    ]
  mfa_configuration = "OPTIONAL"
  tags = {}
  username_attributes = [
    "email"
  ]
  account_recovery_setting {
    recovery_mechanism {
      name = "verified_email"
      priority = 1
    }
  }
  admin_create_user_config {
    allow_admin_create_user_only = false
  }
  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }
  schema {
    attribute_data_type = "String"
    developer_only_attribute = false
    mutable = true
    name = "email"
    required = true
    string_attribute_constraints {
      max_length = "2048"
      min_length = "0"
    }
  }
  software_token_mfa_configuration {
    enabled = true
  }
  username_configuration {
    case_sensitive = false
  }
}

# Get Cognito pool data
data "aws_cognito_user_pools" "budget_boy_data" {
  name = "Budget Boy"
}

# Create API Gateway Authorizer for Cognito pool
resource "aws_api_gateway_authorizer" "bb-cognito" {
  name          = "BudgetBoyCognitoAuthorizer"
  type          = "COGNITO_USER_POOLS"
  rest_api_id   = aws_api_gateway_rest_api.bb_api.id
  provider_arns = data.aws_cognito_user_pools.budget_boy_data.arns
}

# Create Request Validator
resource "aws_api_gateway_request_validator" "parameters" {
  name                        = "Validate query string parameters and headers"
  rest_api_id                 = aws_api_gateway_rest_api.bb_api.id
  validate_request_body       = false
  validate_request_parameters = true
}

# Create API Gateway Methods for each API Gateway resource
resource "aws_api_gateway_method" "get_budgets_method" {
  rest_api_id   = aws_api_gateway_rest_api.bb_api.id
  resource_id   = aws_api_gateway_resource.budgets.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.bb-cognito.id
  authorization_scopes = [
    "aws.cognito.signin.user.admin",
    "email",
    "openid",
    "profile"
  ]
}

resource "aws_api_gateway_integration" "get_budgets_integration" {
  rest_api_id             = aws_api_gateway_rest_api.bb_api.id
  resource_id             = aws_api_gateway_resource.budgets.id
  http_method             = aws_api_gateway_method.get_budgets_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_budgets.invoke_arn
  content_handling = "CONVERT_TO_TEXT"
}



resource "aws_api_gateway_method" "delete_budgets_method" {
  rest_api_id   = aws_api_gateway_rest_api.bb_api.id
  resource_id   = aws_api_gateway_resource.budgets.id
  http_method   = "DELETE"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.bb-cognito.id
  authorization_scopes = [
    "aws.cognito.signin.user.admin",
    "email",
    "openid",
    "profile"
  ]
  request_parameters = {
    "method.request.querystring.BudgetID" = true
  }
  request_validator_id = aws_api_gateway_request_validator.parameters.id
}

resource "aws_api_gateway_integration" "delete_budgets_integration" {
  rest_api_id             = aws_api_gateway_rest_api.bb_api.id
  resource_id             = aws_api_gateway_resource.budgets.id
  http_method             = aws_api_gateway_method.delete_budgets_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.delete_budget.invoke_arn
  content_handling = "CONVERT_TO_TEXT"
}



resource "aws_api_gateway_method" "post_budgets_method" {
  rest_api_id   = aws_api_gateway_rest_api.bb_api.id
  resource_id   = aws_api_gateway_resource.budgets.id
  http_method   = "POST"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.bb-cognito.id
  authorization_scopes = [
    "aws.cognito.signin.user.admin",
    "email",
    "openid",
    "profile"
  ]
}

resource "aws_api_gateway_integration" "post_budgets_integration" {
  rest_api_id             = aws_api_gateway_rest_api.bb_api.id
  resource_id             = aws_api_gateway_resource.budgets.id
  http_method             = aws_api_gateway_method.post_budgets_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.create_budget.invoke_arn
  content_handling = "CONVERT_TO_TEXT"
}



resource "aws_api_gateway_method" "put_budgets_method" {
  rest_api_id   = aws_api_gateway_rest_api.bb_api.id
  resource_id   = aws_api_gateway_resource.budgets.id
  http_method   = "PUT"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.bb-cognito.id
  authorization_scopes = [
    "aws.cognito.signin.user.admin",
    "email",
    "openid",
    "profile"
  ]
  request_parameters = {
    "method.request.querystring.BudgetID" = true
  }
  request_validator_id = aws_api_gateway_request_validator.parameters.id
}

resource "aws_api_gateway_integration" "put_budgets_integration" {
  rest_api_id             = aws_api_gateway_rest_api.bb_api.id
  resource_id             = aws_api_gateway_resource.budgets.id
  http_method             = aws_api_gateway_method.put_budgets_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_budget.invoke_arn
  content_handling = "CONVERT_TO_TEXT"
}



resource "aws_api_gateway_method" "get_budgets_sharing_method" {
  rest_api_id   = aws_api_gateway_rest_api.bb_api.id
  resource_id   = aws_api_gateway_resource.budgets_sharing.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.bb-cognito.id
  authorization_scopes = [
    "aws.cognito.signin.user.admin",
    "email",
    "openid",
    "profile"
  ]
  request_parameters = {
    "method.request.querystring.BudgetID" = true
  }
  request_validator_id = aws_api_gateway_request_validator.parameters.id
}

resource "aws_api_gateway_integration" "get_budgets_sharing_integration" {
  rest_api_id             = aws_api_gateway_rest_api.bb_api.id
  resource_id             = aws_api_gateway_resource.budgets_sharing.id
  http_method             = aws_api_gateway_method.get_budgets_sharing_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_userswithaccess.invoke_arn
  content_handling = "CONVERT_TO_TEXT"
}



resource "aws_api_gateway_method" "put_budgets_sharing_method" {
  rest_api_id   = aws_api_gateway_rest_api.bb_api.id
  resource_id   = aws_api_gateway_resource.budgets_sharing.id
  http_method   = "PUT"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.bb-cognito.id
  authorization_scopes = [
    "aws.cognito.signin.user.admin",
    "email",
    "openid",
    "profile"
  ]
  request_parameters = {
    "method.request.querystring.BudgetID" = true
  }
  request_validator_id = aws_api_gateway_request_validator.parameters.id
}

resource "aws_api_gateway_integration" "put_budgets_sharing_integration" {
  rest_api_id             = aws_api_gateway_rest_api.bb_api.id
  resource_id             = aws_api_gateway_resource.budgets_sharing.id
  http_method             = aws_api_gateway_method.put_budgets_sharing_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.share_budget.invoke_arn
  content_handling = "CONVERT_TO_TEXT"
}



resource "aws_api_gateway_method" "get_categories_method" {
  rest_api_id   = aws_api_gateway_rest_api.bb_api.id
  resource_id   = aws_api_gateway_resource.categories.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.bb-cognito.id
  authorization_scopes = [
    "aws.cognito.signin.user.admin",
    "email",
    "openid",
    "profile"
  ]
  request_parameters = {
    "method.request.querystring.BudgetID" = true
  }
  request_validator_id = aws_api_gateway_request_validator.parameters.id
}

resource "aws_api_gateway_integration" "get_categories_integration" {
  rest_api_id             = aws_api_gateway_rest_api.bb_api.id
  resource_id             = aws_api_gateway_resource.categories.id
  http_method             = aws_api_gateway_method.get_categories_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_categories.invoke_arn
  content_handling = "CONVERT_TO_TEXT"
}



resource "aws_api_gateway_method" "get_reportdata_method" {
  rest_api_id   = aws_api_gateway_rest_api.bb_api.id
  resource_id   = aws_api_gateway_resource.reportdata.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.bb-cognito.id
  authorization_scopes = [
    "aws.cognito.signin.user.admin",
    "email",
    "openid",
    "profile"
  ]
  request_parameters = {
    "method.request.querystring.BudgetID" = true
  }
  request_validator_id = aws_api_gateway_request_validator.parameters.id
}

resource "aws_api_gateway_integration" "get_reportdata_integration" {
  rest_api_id             = aws_api_gateway_rest_api.bb_api.id
  resource_id             = aws_api_gateway_resource.reportdata.id
  http_method             = aws_api_gateway_method.get_reportdata_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_reportdata.invoke_arn
  content_handling = "CONVERT_TO_TEXT"
}

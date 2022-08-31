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
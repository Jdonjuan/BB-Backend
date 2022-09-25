import json
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    print("Event is:", event)
    # Get Token
    Auth = event['headers']['Authorization']
    Token = Auth[7:]
    
    # Get user's email
    cognitoClient = boto3.client('cognito-idp')
    getuserreq = cognitoClient.get_user(
        AccessToken = Token
    )
    UserAttributes = getuserreq['UserAttributes']
    for Attribute in UserAttributes:
        if Attribute['Name'] == 'email':
            UserEmail = Attribute['Value']
            print("User Email is:", UserEmail)
            break
    
    # initiate DynamoDB client and table
    client = boto3.resource("dynamodb")
    table = client.Table("BudgetBoyTable")
    
    # Get Budget information (Parse event body)
    BodyObj = json.loads(event['body'])
    print('Body Object:', BodyObj)
    BudgetItemObj = BodyObj['BudgetItem']
    print('Budget item:', BudgetItemObj)
    BudgetID = BudgetItemObj['BudgetID']['S']
    print('BudgetID', BudgetID)
    
    # Create Budget Item
    BudgetItem = {}
    BudgetItem['PK'] = BudgetItemObj['PK']['S']
    BudgetItem['SK'] = BudgetItemObj['SK']['S']
    BudgetItem['BudgetAmountTotal'] = BudgetItemObj['BudgetAmountTotal']['S']
    BudgetItem['BudgetAmountUsed'] = BudgetItemObj['BudgetAmountUsed']['S']
    BudgetItem['BudgetID'] = BudgetItemObj['BudgetID']['S']
    BudgetItem['BudgetName'] = BudgetItemObj['BudgetName']['S']
    BudgetItem['CurrencySymbol'] = BudgetItemObj['CurrencySymbol']['S']
    BudgetItem['Cycle'] = BudgetItemObj['Cycle']['S']
    BudgetItem['Email'] = BudgetItemObj['Email']['S']
    BudgetItem['IsDefault'] = BudgetItemObj['IsDefault']['BOOL']
    BudgetItem['NextCycleStartDate'] = BudgetItemObj['NextCycleStartDate']['S']
    BudgetItem['TimeZone'] = BudgetItemObj['TimeZone']['S']
    BudgetItem['Type'] = BudgetItemObj['Type']['S']
    BudgetItem['MonthlyCron'] = BudgetItemObj['MonthlyCron']['S']
    
    
    # Create Budget in DynamoDB table
    table.put_item(
        Item = BudgetItem
        )
    
    # Get List of categories, and create the category items in dynamodb
    Categories = BodyObj['Categories']
    for category in Categories:
        # Create Category Items
        CategoryItem = {}
        CategoryItem['PK'] = category['PK']['S']
        CategoryItem['SK'] = category['SK']['S']
        CategoryItem['BudgetID'] = category['BudgetID']['S']
        CategoryItem['CategoryAmountTotal'] = category['CategoryAmountTotal']['S']
        CategoryItem['CategoryAmountUsed'] = category['CategoryAmountUsed']['S']
        CategoryItem['CategoryID'] = category['CategoryID']['S']
        CategoryItem['CategoryName'] = category['CategoryName']['S']
        CategoryItem['CategoryPositionID'] = category['CategoryPositionID']['S']
        CategoryItem['IsRecurring'] = category['IsRecurring']['BOOL']
        CategoryItem['Type'] = category['Type']['S']
        
        # Create Item in DynamoDB
        table.put_item(
            Item = CategoryItem
            )
    
    # Create EventBridge rule with BudgetID as name
    MonthlyCron = BudgetItemObj['MonthlyCron']['S']
    eventclient = boto3.client('events')
    eventclient.put_rule(
        Name = BudgetID,
        ScheduleExpression = f"cron({MonthlyCron})",
        State = 'ENABLED',
        Description = 'NewMonthCleanup',
        RoleArn = 'arn:aws:iam::139654284650:role/BB-EventBridgeRuleRole'
        )
    
    # Create Input 
    Input = {}
    Input['BudgetID'] = BudgetID
    InputJSON = json.dumps(Input)
    # Add targets to event
    eventclient.put_targets(
        Rule = BudgetID,
        Targets = [
            {
                'Id': 'SQSTarget',
                'Arn': 'arn:aws:sqs:us-east-1:139654284650:BB-Clear-Budget-Queue',
                # 'RoleArn': 'arn:aws:iam::139654284650:role/BB-EventBridgeRuleRole',
                'Input': f"{InputJSON}",
                'RetryPolicy': {
                    'MaximumRetryAttempts': 2,
                    'MaximumEventAgeInSeconds': 123
                },
                'DeadLetterConfig': {
                    'Arn': 'arn:aws:sqs:us-east-1:139654284650:BB-Clear-Budget-DLQ'
                }
            }
            ]
        )
    Body = 'Update-Budget-Lambda completed successfully'

    # Construct http response object
    HttpResponseObject = {}
    HttpResponseObject['statusCode'] = 200
    HttpResponseObject['headers'] = {}
    HttpResponseObject['headers']['Content-Type'] = 'application/json'
    HttpResponseObject['headers']['Access-Control-Allow-Origin'] = '*'
    HttpResponseObject['body'] = json.dumps(Body)
    
    return HttpResponseObject

import json
import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
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
    
    # Get all budgets associated with that email
    client = boto3.resource("dynamodb")
    table = client.Table("BudgetBoyTable")
    lookup = f"UEMAIL#{UserEmail}"
    
    Response = table.query(
        KeyConditionExpression = Key('PK').eq(lookup)
        )
        
    Budgets = Response['Items']
    
    # Get budget ID from Query String Parameters
    BudgetID = event['queryStringParameters']['BudgetID']
    print("BudgetID is:", BudgetID)
    
    # if budget id is a budget the user owns, get categories for the budget
    ownsbudget = False
    for budget in Budgets:
        if budget['BudgetID'] == BudgetID:
            ownsbudget = True
            break
    
    # If they own the budget
    if ownsbudget:
        # get every budget item with same BudgetID
        client = boto3.resource("dynamodb")
        table = client.Table("BudgetBoyTable")
        lookup = f"BID#{BudgetID}"
        
        Response = table.query(
            IndexName = "SK-PK-index",
            KeyConditionExpression = "SK = :s",
            ExpressionAttributeValues = { ':s': lookup }
            )
        Budgets = Response['Items']
        
        # fore every budget item with that Budget ID
        for Budget in Budgets:
            # Get Budget information (Parse event body)
            BodyObj = json.loads(event['body'])
            print('Body Object:', BodyObj)
            BudgetItemObj = BodyObj['BudgetItem']
            print('Budget item:', BudgetItemObj)
            BudgetID = BudgetItemObj['BudgetID']['S']
            print('BudgetID', BudgetID)
            
            # Create Budget Item
            BudgetItem = {}
            
            # Change email accordingly
            BudgetItem['PK'] = Budget['PK']
            
            BudgetItem['SK'] = BudgetItemObj['SK']['S']
            BudgetItem['BudgetAmountTotal'] = BudgetItemObj['BudgetAmountTotal']['S']
            BudgetItem['BudgetAmountUsed'] = BudgetItemObj['BudgetAmountUsed']['S']
            BudgetItem['BudgetID'] = BudgetItemObj['BudgetID']['S']
            BudgetItem['BudgetName'] = BudgetItemObj['BudgetName']['S']
            BudgetItem['CurrencySymbol'] = BudgetItemObj['CurrencySymbol']['S']
            BudgetItem['Cycle'] = BudgetItemObj['Cycle']['S']
            
            # Change email accordingly
            BudgetItem['Email'] = Budget['Email']
            
            BudgetItem['IsDefault'] = BudgetItemObj['IsDefault']['BOOL']
            BudgetItem['NextCycleStartDate'] = BudgetItemObj['NextCycleStartDate']['S']
            BudgetItem['TimeZone'] = BudgetItemObj['TimeZone']['S']
            BudgetItem['Type'] = BudgetItemObj['Type']['S']
            BudgetItem['MonthlyCron'] = BudgetItemObj['MonthlyCron']['S']
            
            
            # Create Budget in DynamoDB table
            table.put_item(
                Item = BudgetItem
                )
        
        # Get current categories for that budget (from dynamodb)
        lookup = f"CATBID#{BudgetID}"
        Response = table.query(
            KeyConditionExpression = Key('PK').eq(lookup)
            )
        CurrentCategories = Response['Items']
        # Delete all current categores 
        for CurrentCategory in CurrentCategories:
            table.delete_item(
                Key = {'PK': CurrentCategory['PK'], 'SK': CurrentCategory['SK']}
                )
        
        # For each category in the body object, update the category in dynamodb
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
        
        # Initiate EventBridge Client
        eventclient = boto3.client('events')
        
        # # Get targets for the rule
        # Response = eventclient.list_targets_by_rule(
        #     Rule = BudgetID
        #     )
        # print("Response is:", Response)
        
        # # Delete EventBridge Rule Targets
        # eventclient.remove_targets(
        #     Rule = BudgetID,
        #     Ids = ['SQSTarget'],
        #     Force = True
        #     )
        # # Delete EventBridge Rule itself
        # eventclient.delete_rule(
        #     Name = BudgetID,
        #     Force = True
        #     )
            
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

    return {
        'statusCode': 200,
        'body': json.dumps('Update-Budget-Lambda completed successfully')
    }

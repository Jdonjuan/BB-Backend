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
        
        # Delete all budget items with that Budget ID
        for Budget in Budgets:
            table.delete_item(
                Key = {'PK': Budget['PK'], 'SK': Budget['SK']}
                )
        
        # Get categories for that budget
        lookup = f"CATBID#{BudgetID}"
        Response = table.query(
            KeyConditionExpression = Key('PK').eq(lookup)
            )
        Categories = Response['Items']
        
        # For each category, delete the category
        for Category in Categories:
            table.delete_item(
                Key = {'PK': Category['PK'], 'SK': Category['SK']}
                )
        
        # Get HistoryItems for that budget
        lookup = f"HISTBID#{BudgetID}"
        Response = table.query(
            KeyConditionExpression = Key('PK').eq(lookup)
            )
        HistoryItems = Response['Items']
        
        # For each HistoryItem, delete the Item
        for Item in HistoryItems:
            table.delete_item(
                Key = {'PK': Item['PK'], 'SK': Item['SK']}
                )
        
        
        # Initiate EventBridge Client
        eventclient = boto3.client('events')
        
        # # Get targets for the rule
        # Response = eventclient.list_targets_by_rule(
        #     Rule = BudgetID
        #     )
        # print("Response is:", Response)
        
        # Delete EventBridge Rule Targets
        eventclient.remove_targets(
            Rule = BudgetID,
            Ids = ['SQSTarget'],
            Force = True
            )
        # Delete EventBridge Rule itself
        eventclient.delete_rule(
            Name = BudgetID,
            Force = True
            )
            
    return {
        'statusCode': 200,
        'body': json.dumps('BB-Delete-Budget-Lambda completed successfully')
    }

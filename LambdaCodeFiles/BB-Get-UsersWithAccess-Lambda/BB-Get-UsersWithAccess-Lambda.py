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
        # Get every budget item with same BudgetID
        client = boto3.resource("dynamodb")
        table = client.Table("BudgetBoyTable")
        lookup = f"BID#{BudgetID}"
        
        Response = table.query(
            IndexName = "SK-PK-index",
            KeyConditionExpression = "SK = :s",
            ExpressionAttributeValues = { ':s': lookup }
            )
        Budgets = Response['Items']
        
        EmailList = []
        for Budget in Budgets:
            # print(Budget["Email"])
            EmailList.append(Budget["Email"])
        
        # print("Email List:", EmailList)
        
        # Construct body of response
        Body = {}
        Body['EmailsWithAccess'] = EmailList
        # print("Body is:", Body)
        
        # Construct http response object
        HttpResponseObject = {}
        HttpResponseObject['statusCode'] = 200
        HttpResponseObject['headers'] = {}
        HttpResponseObject['headers']['Content-Type'] = 'application/json'
        HttpResponseObject['body'] = json.dumps(Body)
    
    
    
    return HttpResponseObject

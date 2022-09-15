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
    
    if ownsbudget:
        lookup = f"CATBID#{BudgetID}"
        Response = table.query(
            KeyConditionExpression = Key('PK').eq(lookup)
            )
        Categories = Response['Items']
    else:
        Categories = {}
    
    # Construct body of response
    Body = {}
    Body['Categories'] = Categories
    
    # Construct http response object
    HttpResponseObject = {}
    HttpResponseObject['statusCode'] = 200
    HttpResponseObject['headers'] = {}
    HttpResponseObject['headers']['Content-Type'] = 'application/json'
    HttpResponseObject['headers']['Access-Control-Allow-Origin'] = '*'
    HttpResponseObject['body'] = json.dumps(Body)
    
    
    
    return HttpResponseObject
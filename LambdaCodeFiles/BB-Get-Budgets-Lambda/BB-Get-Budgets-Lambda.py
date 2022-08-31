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
    
    
    # Construct body of response
    Body = {}
    Body['Budgets'] = Budgets
    
    # Construct http response object
    HttpResponseObject = {}
    HttpResponseObject['statusCode'] = 200
    HttpResponseObject['headers'] = {}
    HttpResponseObject['headers']['Content-Type'] = 'application/json'
    HttpResponseObject['body'] = json.dumps(Body)
    
    
    
    return HttpResponseObject

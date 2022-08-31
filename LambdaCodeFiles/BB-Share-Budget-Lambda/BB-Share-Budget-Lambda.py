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
        # Get body as object
        BodyObj = json.loads(event['body'])
        
        # Get AccessList from body
        EmailsWithAccess = BodyObj["EmailsWithAccess"]
        
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
        
        for Budget in Budgets:
            if Budget["Email"] not in EmailsWithAccess:
                table.delete_item(
                    Key = {'PK': Budget['PK'], 'SK': Budget['SK']}
                    )
        # Create item (share) if it doesn't exist (Not alreadyShared)
        for Email in EmailsWithAccess:
            # Get Budget information (Parse event body)
            BodyObj = json.loads(event['body'])
            print('Body Object:', BodyObj)
            BudgetItemObj = BodyObj['BudgetItem']
            print('Budget item:', BudgetItemObj)
            BudgetID = BudgetItemObj['BudgetID']['S']
            print('BudgetID', BudgetID)
            
            # Create New Partition Key
            PK = f"UEMAIL#{Email}"
            
            # Create Budget Item
            BudgetItem = {}
            
            # Change email accordingly
            BudgetItem['PK'] = PK
            
            BudgetItem['SK'] = BudgetItemObj['SK']['S']
            BudgetItem['BudgetAmountTotal'] = BudgetItemObj['BudgetAmountTotal']['S']
            BudgetItem['BudgetAmountUsed'] = BudgetItemObj['BudgetAmountUsed']['S']
            BudgetItem['BudgetID'] = BudgetItemObj['BudgetID']['S']
            BudgetItem['BudgetName'] = BudgetItemObj['BudgetName']['S']
            BudgetItem['CurrencySymbol'] = BudgetItemObj['CurrencySymbol']['S']
            BudgetItem['Cycle'] = BudgetItemObj['Cycle']['S']
            
            # Change email accordingly
            BudgetItem['Email'] = Email
            
            BudgetItem['IsDefault'] = BudgetItemObj['IsDefault']['BOOL']
            BudgetItem['NextCycleStartDate'] = BudgetItemObj['NextCycleStartDate']['S']
            BudgetItem['TimeZone'] = BudgetItemObj['TimeZone']['S']
            BudgetItem['Type'] = BudgetItemObj['Type']['S']
            BudgetItem['MonthlyCron'] = BudgetItemObj['MonthlyCron']['S']
            
            
            # Create Budget in DynamoDB table
            table.put_item(
                Item = BudgetItem
                )
        
    return {
        'statusCode': 200,
        'body': json.dumps('BB-Share-Budget-Lambda completed successfully')
    }

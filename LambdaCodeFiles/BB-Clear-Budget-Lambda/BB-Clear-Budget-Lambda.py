import json
from datetime import datetime,timezone
import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    # Get BudgetID from event
    body = json.loads(event['Records'][0]['body'])
    print("event is:", event)
    BudgetID = body['BudgetID']
    print("Budget ID:", BudgetID)
    
    # Create timestamp in UTC
    UtcTimestamp = datetime.now(timezone.utc)
    print ("UTC timestamp:", UtcTimestamp)
    
    
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
    
    # Clear BudgetAmountUsed for the budget Items with same BudgetID
    for Budget in Budgets:
        table.update_item(
            Key = {'PK': Budget['PK'], 'SK': Budget['SK']},
            UpdateExpression = "set BudgetAmountUsed=:a",
            ExpressionAttributeValues = { ':a': '0' }
            )
    
    # Get all categories for the budget
    lookup = f"CATBID#{BudgetID}"
    Response = table.query(
        KeyConditionExpression = Key('PK').eq(lookup)
        )
    Categories = Response['Items']
    print(Categories)
    # For every category, create a history item
    #   BudgetID, Timestamp, CategoryID, CategoryAmountUsed
    for Category in Categories:
        CategoryID = Category['CategoryID']
        PK = f"HISTBID#{BudgetID}"
        SK = f"HISTCID#{CategoryID}HISTTIME#{UtcTimestamp}"
        CatAmountUsed = Category['CategoryAmountUsed']
        
        HistItem = {}
        HistItem['PK'] = PK
        HistItem['SK'] = SK
        HistItem['BudgetID'] = BudgetID
        HistItem['CategoryID'] = CategoryID
        HistItem['Timestamp'] = str(UtcTimestamp)
        HistItem['CategoryAmountUsed'] = CatAmountUsed
        HistItem['Type'] = 'CategoryHistory'
        
        # Create Category History item in dynamodb
        table.put_item(
            Item = HistItem
            )
        
        # Clear CategoryAmountUsed for each category if the category is not recurring
        if Category["IsRecurring"] == False:
            table.update_item(
                Key = {'PK': Category['PK'], 'SK': Category['SK']},
                UpdateExpression = "set CategoryAmountUsed=:a",
                ExpressionAttributeValues = { ':a': '0' }
                )
            
    return {
        'statusCode': 200,
        'body': json.dumps('Clear-Budget-Lambda completed successfully')
    }

import boto3

# Create SQS client
sqs = boto3.client('sqs')

queue_url = 'https://sqs.us-east-1.amazonaws.com/139654284650/BB-Clear-Budget-Queue'

# # Enable long polling on an existing SQS queue
# sqs.set_queue_attributes(
#     QueueUrl=queue_url,
#     Attributes={'ReceiveMessageWaitTimeSeconds': '20'}
# )

response = sqs.get_queue_attributes(
    QueueUrl = queue_url,
    AttributeNames = ['All']
)

print(response)
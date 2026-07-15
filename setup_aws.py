import boto3
from config import Config
import time

def setup_dynamodb(dynamodb):
    table_name = Config.DYNAMODB_LOG_TABLE
    try:
        # Check if table exists
        dynamodb.describe_table(TableName=table_name)
        print(f"Table {table_name} already exists.")
    except dynamodb.exceptions.ResourceNotFoundException:
        print(f"Creating DynamoDB table: {table_name}...")
        try:
            dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'log_id', 'KeyType': 'HASH'}  # Partition key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'log_id', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            # Wait for table to be active
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            print(f"Table {table_name} created successfully!")
        except Exception as e:
            print(f"Error creating table: {str(e)}")

def setup_sns(sns):
    topic_name = Config.SNS_TOPIC_NAME
    try:
        print(f"Creating SNS topic: {topic_name}...")
        response = sns.create_topic(Name=topic_name)
        print(f"Topic created successfully! ARN: {response['TopicArn']}")
        
        # Save ARN to a local file so the Flask app can read it if needed
        with open('.sns_arn', 'w') as f:
            f.write(response['TopicArn'])
    except Exception as e:
        print(f"Error creating SNS topic: {str(e)}")

if __name__ == '__main__':
    print("Starting AWS Resource Setup for Capstone Project...")
    
    # Use standard default session
    session = boto3.Session(region_name=Config.AWS_REGION)
    
    dynamodb = session.client('dynamodb')
    setup_dynamodb(dynamodb)
    
    sns = session.client('sns')
    setup_sns(sns)
    
    print("Setup complete.")

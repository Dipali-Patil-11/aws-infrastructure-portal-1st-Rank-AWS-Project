from datetime import datetime
from utils.aws_client import get_aws_resource
from config import Config
import uuid

def log_activity(user, resource, action, status):
    """
    Logs user activity to DynamoDB.
    """
    try:
        dynamodb = get_aws_resource('dynamodb')
        if not dynamodb:
            print("DynamoDB resource not available. Skipping log.")
            return

        table = dynamodb.Table(Config.DYNAMODB_LOG_TABLE)
        
        timestamp = datetime.utcnow().isoformat()
        
        table.put_item(
            Item={
                'log_id': str(uuid.uuid4()),
                'timestamp': timestamp,
                'user': user,
                'resource': resource,
                'action': action,
                'status': status
            }
        )
    except Exception as e:
        print(f"Failed to log activity: {str(e)}")
        # In a real app, you might want to retry or write to a local fallback log file

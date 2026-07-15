import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-capstone-key'
    AWS_REGION = os.environ.get('AWS_REGION') or 'ap-south-1'
    DYNAMODB_LOG_TABLE = os.environ.get('DYNAMODB_LOG_TABLE') or 'CloudPortalActivityLogs'
    SNS_TOPIC_NAME = os.environ.get('SNS_TOPIC_NAME') or 'CloudPortalNotifications'

import boto3
from flask import session
from session_store import ACTIVE_SESSIONS

def get_aws_client(service_name):
    """
    Returns a boto3 client for the specified service using the logged-in user's temporary credentials.
    """
    try:
        session_id = session.get('session_id')
        user_creds = ACTIVE_SESSIONS.get(session_id)
        
        if not user_creds:
            print("No active AWS session found for user.")
            return None
            
        return boto3.client(
            service_name,
            aws_access_key_id=user_creds['access_key'],
            aws_secret_access_key=user_creds['secret_key'],
            aws_session_token=user_creds['session_token'],
            region_name=user_creds['region']
        )
    except Exception as e:
        print(f"Error creating boto3 client for {service_name}: {str(e)}")
        return None

def get_aws_resource(service_name):
    """
    Returns a boto3 resource for the specified service using the logged-in user's temporary credentials.
    """
    try:
        session_id = session.get('session_id')
        user_creds = ACTIVE_SESSIONS.get(session_id)
        
        if not user_creds:
            print("No active AWS session found for user.")
            return None
            
        return boto3.resource(
            service_name,
            aws_access_key_id=user_creds['access_key'],
            aws_secret_access_key=user_creds['secret_key'],
            aws_session_token=user_creds['session_token'],
            region_name=user_creds['region']
        )
    except Exception as e:
        print(f"Error creating boto3 resource for {service_name}: {str(e)}")
        return None

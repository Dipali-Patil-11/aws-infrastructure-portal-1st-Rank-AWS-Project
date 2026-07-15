from flask import Blueprint, jsonify, request, session
from utils.aws_client import get_aws_client
from utils.logger import log_activity
from datetime import datetime

logs_bp = Blueprint('logs', __name__)
from config import Config

def get_user():
    return session.get('username', 'System')

@logs_bp.route('/', methods=['GET'])
def get_logs():
    dynamodb = get_aws_client('dynamodb')
    if not dynamodb: return jsonify({'error': 'Failed to connect to DynamoDB'}), 500
    
    try:
        response = dynamodb.scan(TableName=Config.DYNAMODB_LOG_TABLE)
        items = response.get('Items', [])
        
        # Convert DynamoDB types to plain dict
        logs = []
        for item in items:
            logs.append({
                'log_id': item['log_id']['S'],
                'timestamp': item['timestamp']['S'],
                'user': item['user']['S'],
                'resource': item['resource']['S'],
                'action': item['action']['S'],
                'status': item['status']['S']
            })
            
        # Sort by timestamp descending
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

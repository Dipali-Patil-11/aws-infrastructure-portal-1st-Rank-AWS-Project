from flask import Blueprint, jsonify
from utils.aws_client import get_aws_client

dynamodb_bp = Blueprint('dynamodb', __name__)

@dynamodb_bp.route('/list', methods=['GET'])
def list_tables():
    dynamo = get_aws_client('dynamodb')
    if not dynamo:
        return jsonify({'error': 'Failed to connect to DynamoDB'}), 500
        
    try:
        response = dynamo.list_tables()
        tables = []
        for table_name in response.get('TableNames', []):
            desc = dynamo.describe_table(TableName=table_name)['Table']
            tables.append({
                'name': table_name,
                'status': desc['TableStatus'],
                'item_count': desc.get('ItemCount', 0),
                'size_bytes': desc.get('TableSizeBytes', 0),
                'creation_date': desc['CreationDateTime'].strftime("%Y-%m-%d %H:%M:%S") if 'CreationDateTime' in desc else 'N/A'
            })
        return jsonify(tables)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

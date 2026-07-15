from api.lambda_auto import apigw_bp
# We merged apigw_bp into lambda_auto.py for simplicity but the route expects it to be in its own file
# I will redefine it here properly to keep files clean.
from flask import Blueprint, jsonify, request, session
from utils.aws_client import get_aws_client
from utils.logger import log_activity

apigw_bp = Blueprint('api_gateway', __name__)
def get_user(): return session.get('username', 'System')

@apigw_bp.route('/list', methods=['GET'])
def list_apis():
    apigw = get_aws_client('apigateway')
    if not apigw: return jsonify({'error': 'Failed to connect to API Gateway'}), 500
    try:
        response = apigw.get_rest_apis()
        apis = []
        for api in response.get('items', []):
            apis.append({
                'id': api['id'],
                'name': api['name'],
                'description': api.get('description', 'N/A'),
                'created': api['createdDate'].strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify(apis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

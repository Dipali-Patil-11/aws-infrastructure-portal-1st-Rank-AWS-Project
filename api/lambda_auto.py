from flask import Blueprint, jsonify, request, session
from utils.aws_client import get_aws_client
from utils.logger import log_activity
from config import Config
import json

lambda_bp = Blueprint('lambda', __name__)
def get_user(): return session.get('username', 'System')

@lambda_bp.route('/list', methods=['GET'])
def list_functions():
    lam = get_aws_client('lambda')
    if not lam: return jsonify({'error': 'Failed to connect to Lambda'}), 500
    try:
        response = lam.list_functions()
        functions = []
        for fn in response['Functions']:
            functions.append({
                'name': fn['FunctionName'],
                'runtime': fn['Runtime'],
                'state': fn.get('State', 'Active'),
                'last_modified': fn['LastModified'],
                'role': fn['Role']
            })
        return jsonify(functions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

apigw_bp = Blueprint('api_gateway', __name__)

@apigw_bp.route('/list', methods=['GET'])
def list_apis():
    apigw = get_aws_client('apigateway')
    if not apigw: return jsonify({'error': 'Failed to connect to API Gateway'}), 500
    try:
        response = apigw.get_rest_apis()
        apis = []
        for api in response['items']:
            apis.append({
                'id': api['id'],
                'name': api['name'],
                'created': api['createdDate'].strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify(apis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

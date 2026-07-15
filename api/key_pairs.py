from flask import Blueprint, jsonify, request, session
from utils.aws_client import get_aws_client
from utils.logger import log_activity

kp_bp = Blueprint('key_pairs', __name__)

def get_user():
    return session.get('username', 'System')

@kp_bp.route('/list', methods=['GET'])
def list_key_pairs():
    ec2 = get_aws_client('ec2')
    if not ec2: return jsonify({'error': 'Failed to connect to EC2'}), 500
    
    try:
        response = ec2.describe_key_pairs()
        kps = []
        for kp in response['KeyPairs']:
            kps.append({
                'name': kp['KeyName'],
                'fingerprint': kp.get('KeyFingerprint', 'N/A'),
                'type': kp.get('KeyType', 'N/A'),
                'id': kp.get('KeyPairId', 'N/A'),
                'creation_date': kp.get('CreateTime', 'N/A').strftime("%Y-%m-%d %H:%M:%S") if 'CreateTime' in kp else 'N/A'
            })
        return jsonify(kps)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@kp_bp.route('/create', methods=['POST'])
def create_key_pair():
    data = request.json
    key_name = data.get('key_name')
    ec2 = get_aws_client('ec2')
    
    try:
        response = ec2.create_key_pair(KeyName=key_name, KeyType='rsa', KeyFormat='pem')
        log_activity(get_user(), 'KeyPair', f'Created Key Pair {key_name}', 'Success')
        # Return the private key material so the frontend can download it
        return jsonify({
            'message': f'Key Pair {key_name} created',
            'key_material': response['KeyMaterial'],
            'key_name': key_name
        })
    except Exception as e:
        log_activity(get_user(), 'KeyPair', f'Create Key Pair failed for {key_name}', f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@kp_bp.route('/delete', methods=['DELETE'])
def delete_key_pair():
    key_name = request.json.get('key_name')
    ec2 = get_aws_client('ec2')
    try:
        ec2.delete_key_pair(KeyName=key_name)
        log_activity(get_user(), 'KeyPair', f'Deleted Key Pair {key_name}', 'Success')
        return jsonify({'message': f'Key Pair {key_name} deleted'})
    except Exception as e:
        log_activity(get_user(), 'KeyPair', f'Delete Key Pair failed for {key_name}', f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

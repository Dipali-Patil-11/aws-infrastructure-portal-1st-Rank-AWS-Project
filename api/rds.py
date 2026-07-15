from flask import Blueprint, jsonify
from utils.aws_client import get_aws_client

rds_bp = Blueprint('rds', __name__)

@rds_bp.route('/list', methods=['GET'])
def list_instances():
    rds = get_aws_client('rds')
    if not rds:
        return jsonify({'error': 'Failed to connect to RDS'}), 500
        
    try:
        response = rds.describe_db_instances()
        instances = []
        for db in response.get('DBInstances', []):
            instances.append({
                'id': db['DBInstanceIdentifier'],
                'engine': db['Engine'],
                'engine_version': db['EngineVersion'],
                'status': db['DBInstanceStatus'],
                'class': db['DBInstanceClass'],
                'endpoint': db.get('Endpoint', {}).get('Address', 'N/A'),
                'storage': f"{db.get('AllocatedStorage', 0)} GB"
            })
        return jsonify(instances)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

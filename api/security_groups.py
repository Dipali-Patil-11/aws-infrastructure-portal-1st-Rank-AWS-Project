from flask import Blueprint, jsonify, request, session
from utils.aws_client import get_aws_client
from utils.logger import log_activity

sg_bp = Blueprint('security_groups', __name__)

def get_user():
    return session.get('username', 'System')

@sg_bp.route('/list', methods=['GET'])
def list_sgs():
    ec2 = get_aws_client('ec2')
    if not ec2: return jsonify({'error': 'Failed to connect to EC2'}), 500
    
    try:
        response = ec2.describe_security_groups()
        sgs = []
        for sg in response['SecurityGroups']:
            sgs.append({
                'id': sg['GroupId'],
                'name': sg['GroupName'],
                'description': sg.get('Description', 'N/A'),
                'vpc_id': sg.get('VpcId', 'N/A'),
                'inbound_rules': len(sg.get('IpPermissions', [])),
                'outbound_rules': len(sg.get('IpPermissionsEgress', []))
            })
        return jsonify(sgs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sg_bp.route('/create', methods=['POST'])
def create_sg():
    data = request.json
    name = data.get('group_name')
    desc = data.get('description', 'Created via Cloud Portal')
    vpc_id = data.get('vpc_id')
    ec2 = get_aws_client('ec2')
    
    try:
        if vpc_id:
            response = ec2.create_security_group(GroupName=name, Description=desc, VpcId=vpc_id)
        else:
            response = ec2.create_security_group(GroupName=name, Description=desc)
        group_id = response['GroupId']
        log_activity(get_user(), 'SecurityGroup', f'Created SG {group_id} ({name})', 'Success')
        return jsonify({'message': f'Security Group {name} created', 'group_id': group_id})
    except Exception as e:
        log_activity(get_user(), 'SecurityGroup', f'Create SG failed for {name}', f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@sg_bp.route('/delete', methods=['DELETE'])
def delete_sg():
    group_id = request.json.get('group_id')
    ec2 = get_aws_client('ec2')
    try:
        ec2.delete_security_group(GroupId=group_id)
        log_activity(get_user(), 'SecurityGroup', f'Deleted SG {group_id}', 'Success')
        return jsonify({'message': f'Security Group {group_id} deleted'})
    except Exception as e:
        log_activity(get_user(), 'SecurityGroup', f'Delete SG failed for {group_id}', f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

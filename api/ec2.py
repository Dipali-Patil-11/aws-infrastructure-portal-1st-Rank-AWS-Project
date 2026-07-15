from flask import Blueprint, jsonify, request, session
from utils.aws_client import get_aws_client
from utils.logger import log_activity

ec2_bp = Blueprint('ec2', __name__)

def get_user():
    return session.get('username', 'System')

@ec2_bp.route('/list', methods=['GET'])
def list_instances():
    ec2 = get_aws_client('ec2')
    if not ec2:
        return jsonify({'error': 'Failed to connect to EC2'}), 500
    
    try:
        response = ec2.describe_instances()
        instances = []
        for reservation in response['Reservations']:
            for inst in reservation['Instances']:
                name = 'Unnamed'
                if 'Tags' in inst:
                    for tag in inst['Tags']:
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                instances.append({
                    'id': inst['InstanceId'],
                    'name': name,
                    'type': inst['InstanceType'],
                    'state': inst['State']['Name'],
                    'public_ip': inst.get('PublicIpAddress', 'N/A'),
                    'private_ip': inst.get('PrivateIpAddress', 'N/A'),
                    'launch_time': inst['LaunchTime'].strftime("%Y-%m-%d %H:%M:%S") if 'LaunchTime' in inst else 'N/A',
                    'ami': inst['ImageId'],
                    'az': inst['Placement']['AvailabilityZone']
                })
        return jsonify(instances)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ec2_bp.route('/launch', methods=['POST'])
def launch_instance():
    data = request.json
    ec2 = get_aws_client('ec2')
    if not ec2: return jsonify({'error': 'AWS Connection Failed'}), 500
    
    try:
        response = ec2.run_instances(
            ImageId=data.get('ami', 'ami-02b1e663aa8e2a28a'), # default amazon linux 2 ap-south-1
            InstanceType=data.get('instance_type', 't2.micro'),
            MinCount=1,
            MaxCount=1,
            KeyName=data.get('key_pair'),
            SecurityGroupIds=[data.get('security_group')] if data.get('security_group') else [],
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': data.get('name', 'Capstone-Instance')}]
            }]
        )
        instance_id = response['Instances'][0]['InstanceId']
        log_activity(get_user(), 'EC2', f'Launched instance {instance_id}', 'Success')
        return jsonify({'message': f'Instance {instance_id} launching', 'instance_id': instance_id})
    except Exception as e:
        log_activity(get_user(), 'EC2', 'Launch instance failed', f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@ec2_bp.route('/action', methods=['POST'])
def instance_action():
    data = request.json
    action = data.get('action')
    instance_ids = data.get('instance_ids', [])
    ec2 = get_aws_client('ec2')
    
    try:
        if action == 'start':
            ec2.start_instances(InstanceIds=instance_ids)
        elif action == 'stop':
            ec2.stop_instances(InstanceIds=instance_ids)
        elif action == 'restart':
            ec2.reboot_instances(InstanceIds=instance_ids)
        elif action == 'terminate':
            ec2.terminate_instances(InstanceIds=instance_ids)
        else:
            return jsonify({'error': 'Invalid action'}), 400
            
        log_activity(get_user(), 'EC2', f'{action.capitalize()} instances {instance_ids}', 'Success')
        return jsonify({'message': f'Successfully executed {action} on {len(instance_ids)} instances'})
    except Exception as e:
        log_activity(get_user(), 'EC2', f'{action.capitalize()} instance failed', f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

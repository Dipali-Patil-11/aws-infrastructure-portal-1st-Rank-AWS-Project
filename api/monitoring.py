from flask import Blueprint, jsonify, request, session
from utils.aws_client import get_aws_client
from utils.logger import log_activity
from datetime import datetime, timedelta

monitor_bp = Blueprint('monitoring', __name__)
from config import Config

@monitor_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Fetch aggregated basic metrics for dashboard"""
    cw = get_aws_client('cloudwatch')
    ec2 = get_aws_client('ec2')
    if not cw or not ec2: return jsonify({'error': 'Failed to connect to AWS services'}), 500
    
    try:
        from session_store import ACTIVE_SESSIONS
        session_id = session.get('session_id')
        user_region = ACTIVE_SESSIONS.get(session_id, {}).get('region', Config.AWS_REGION)

        # Get count of running EC2 instances
        ec2_res = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        running_ec2 = sum(len(res['Instances']) for res in ec2_res['Reservations'])
        
        # Get count of stopped EC2 instances
        ec2_stopped_res = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
        stopped_ec2 = sum(len(res['Instances']) for res in ec2_stopped_res['Reservations'])
        # S3 bucket count
        s3 = get_aws_client('s3')
        s3_buckets = len(s3.list_buckets()['Buckets'])
        
        # API Gateway count
        apigw = get_aws_client('apigateway')
        api_gateways = len(apigw.get_rest_apis().get('items', []))
        
        # Lambda functions count
        lam = get_aws_client('lambda')
        lambda_functions = len(lam.list_functions().get('Functions', []))
        
        payload = {
            'running_ec2': running_ec2,
            'stopped_ec2': stopped_ec2,
            's3_buckets': s3_buckets,
            'api_gateways': api_gateways,
            'lambda_functions': lambda_functions,
            'region': user_region
        }
        with open('debug_payload.txt', 'w') as f:
            f.write(str(payload))
        print(f"DEBUG METRICS PAYLOAD: {payload}")
        return jsonify(payload)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitor_bp.route('/storage_usage', methods=['GET'])
def get_storage_usage():
    cw = get_aws_client('cloudwatch')
    s3 = get_aws_client('s3')
    if not cw or not s3: return jsonify({'error': 'Failed to connect'}), 500
    
    try:
        buckets = s3.list_buckets()['Buckets']
        labels = []
        data = []
        
        # Get storage for top 5 buckets
        for b in buckets[:5]:
            response = cw.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': b['Name']},
                    {'Name': 'StorageType', 'Value': 'StandardStorage'}
                ],
                StartTime=datetime.utcnow() - timedelta(days=2),
                EndTime=datetime.utcnow(),
                Period=86400,
                Statistics=['Average']
            )
            size_gb = 0
            if response['Datapoints']:
                dp = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])[-1]
                size_gb = dp['Average'] / (1024**3)
            
            labels.append(b['Name'])
            data.append(round(size_gb, 4))
            
        return jsonify({'labels': labels, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitor_bp.route('/ec2_cpu', methods=['GET'])
def get_ec2_cpu_metrics():
    cw = get_aws_client('cloudwatch')
    instance_id = request.args.get('instance_id')
    
    if not instance_id:
        return jsonify({'error': 'Missing instance_id parameter'}), 400
        
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        response = cw.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300, # 5 minutes
            Statistics=['Average']
        )
        
        datapoints = response['Datapoints']
        datapoints.sort(key=lambda x: x['Timestamp'])
        
        times = [dp['Timestamp'].strftime('%H:%M') for dp in datapoints]
        values = [round(dp['Average'], 2) for dp in datapoints]
        
        return jsonify({
            'times': times,
            'values': values
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitor_bp.route('/rds_stats', methods=['GET'])
def get_rds_stats():
    rds = get_aws_client('rds')
    if not rds: return jsonify({'error': 'Connection failed'}), 500
    try:
        instances = rds.describe_db_instances().get('DBInstances', [])
        available = sum(1 for db in instances if db['DBInstanceStatus'] == 'available')
        stopped = sum(1 for db in instances if db['DBInstanceStatus'] == 'stopped')
        other = len(instances) - available - stopped
        return jsonify({'available': available, 'stopped': stopped, 'other': other})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@monitor_bp.route('/dynamo_stats', methods=['GET'])
def get_dynamo_stats():
    dynamo = get_aws_client('dynamodb')
    if not dynamo: return jsonify({'error': 'Connection failed'}), 500
    try:
        tables = dynamo.list_tables().get('TableNames', [])
        labels = []
        data = []
        for t in tables[:5]:
            desc = dynamo.describe_table(TableName=t)['Table']
            labels.append(t)
            data.append(desc.get('ItemCount', 0))
        return jsonify({'labels': labels, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

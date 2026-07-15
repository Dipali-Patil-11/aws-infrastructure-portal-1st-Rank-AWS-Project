from flask import Blueprint, jsonify, request, session
from utils.aws_client import get_aws_client
from config import Config
from utils.logger import log_activity

sns_bp = Blueprint('notifications', __name__)

def get_user(): return session.get('username', 'System')

def get_topic_arn():
    try:
        with open('.sns_arn', 'r') as f:
            return f.read().strip()
    except:
        return None

@sns_bp.route('/subscriptions', methods=['GET'])
def list_subscriptions():
    sns = get_aws_client('sns')
    topic_arn = get_topic_arn()
    if not sns or not topic_arn: return jsonify({'error': 'SNS Topic not configured'}), 400
    
    try:
        response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
        subs = []
        for sub in response.get('Subscriptions', []):
            subs.append({
                'endpoint': sub['Endpoint'],
                'protocol': sub['Protocol'],
                'status': sub['SubscriptionArn'] if 'PendingConfirmation' not in sub['SubscriptionArn'] else 'Pending'
            })
        return jsonify(subs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sns_bp.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.json.get('email')
    sns = get_aws_client('sns')
    topic_arn = get_topic_arn()
    
    try:
        sns.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email
        )
        log_activity(get_user(), 'SNS', f'Subscribed {email}', 'Success')
        return jsonify({'message': f'Subscription request sent to {email}. Please confirm.'})
    except Exception as e:
        log_activity(get_user(), 'SNS', f'Subscribe failed for {email}', f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

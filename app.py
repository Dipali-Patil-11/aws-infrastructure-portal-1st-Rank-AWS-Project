from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from config import Config
import os
import boto3
import uuid
from session_store import ACTIVE_SESSIONS
app = Flask(__name__)
app.config.from_object(Config)

# Import Blueprints for APIs (we will create these next)
from api.ec2 import ec2_bp
from api.s3 import s3_bp
from api.security_groups import sg_bp
from api.key_pairs import kp_bp
from api.lambda_auto import lambda_bp
from api.api_gateway import apigw_bp
from api.monitoring import monitor_bp
from api.notifications import sns_bp
from api.logs import logs_bp
from api.cost import cost_bp
from api.rds import rds_bp
from api.dynamodb import dynamodb_bp

# Register Blueprints
app.register_blueprint(ec2_bp, url_prefix='/api/ec2')
app.register_blueprint(s3_bp, url_prefix='/api/s3')
app.register_blueprint(sg_bp, url_prefix='/api/security_groups')
app.register_blueprint(kp_bp, url_prefix='/api/key_pairs')
app.register_blueprint(lambda_bp, url_prefix='/api/lambda')
app.register_blueprint(apigw_bp, url_prefix='/api/api_gateway')
app.register_blueprint(monitor_bp, url_prefix='/api/monitoring')
app.register_blueprint(sns_bp, url_prefix='/api/notifications')
app.register_blueprint(logs_bp, url_prefix='/api/logs')
app.register_blueprint(cost_bp, url_prefix='/api/cost')
app.register_blueprint(rds_bp, url_prefix='/api/rds')
app.register_blueprint(dynamodb_bp, url_prefix='/api/dynamodb')


# --- Frontend Routes ---

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        access_key = request.form.get('access_key')
        secret_key = request.form.get('secret_key')
        region = request.form.get('region')
        
        try:
            # 1. Validate credentials with STS
            sts = boto3.client('sts', 
                               aws_access_key_id=access_key, 
                               aws_secret_access_key=secret_key, 
                               region_name=region)
            identity = sts.get_caller_identity()
            
            # 2. Get Temporary Session Credentials (valid for 1 hour)
            temp_creds = sts.get_session_token(DurationSeconds=3600)['Credentials']
            
            # 3. Store in memory, not permanently
            session_id = str(uuid.uuid4())
            ACTIVE_SESSIONS[session_id] = {
                'access_key': temp_creds['AccessKeyId'],
                'secret_key': temp_creds['SecretAccessKey'],
                'session_token': temp_creds['SessionToken'],
                'region': region,
                'account_id': identity['Account'],
                'arn': identity['Arn']
            }
            
            session['session_id'] = session_id
            session['logged_in'] = True
            session['username'] = identity['Arn'].split('/')[-1]
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            return render_template('login.html', error=f'Authentication failed: {str(e)}')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session_id = session.get('session_id')
    if session_id in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[session_id]
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    session_id = session.get('session_id')
    user_creds = ACTIVE_SESSIONS.get(session_id)
    if not user_creds:
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', 
                           account_id=user_creds['account_id'],
                           arn=user_creds['arn'],
                           region=user_creds['region'])

@app.route('/ec2')
def ec2_management():
    if 'logged_in' not in session: return redirect(url_for('login'))
    return render_template('ec2.html')

@app.route('/s3')
def s3_management():
    if 'session_id' not in session:
        return redirect(url_for('login'))
    return render_template('s3.html')

@app.route('/rds')
def rds_management():
    if 'session_id' not in session:
        return redirect(url_for('login'))
    return render_template('rds.html')

@app.route('/dynamodb')
def dynamodb_management():
    if 'session_id' not in session:
        return redirect(url_for('login'))
    return render_template('dynamodb.html')

@app.route('/security-groups')
def security_groups():
    if 'logged_in' not in session: return redirect(url_for('login'))
    return render_template('security_groups.html')

@app.route('/key-pairs')
def key_pairs():
    if 'logged_in' not in session: return redirect(url_for('login'))
    return render_template('key_pairs.html')

@app.route('/lambda')
def lambda_automation():
    if 'logged_in' not in session: return redirect(url_for('login'))
    return render_template('lambda.html')

@app.route('/api-gateway')
def api_gateway():
    if 'logged_in' not in session: return redirect(url_for('login'))
    return render_template('api_gateway.html')

@app.route('/monitoring')
def monitoring():
    if 'logged_in' not in session: return redirect(url_for('login'))
    return render_template('monitoring.html')

@app.route('/notifications')
def notifications():
    if 'logged_in' not in session: return redirect(url_for('login'))
    return render_template('notifications.html')

@app.route('/activity-logs')
def activity_logs():
    if 'logged_in' not in session: return redirect(url_for('login'))
    return render_template('logs.html')

@app.route('/cost-dashboard')
def cost_dashboard():
    if 'logged_in' not in session: return redirect(url_for('login'))
    return render_template('cost.html')

@app.route('/reports')
def reports():
    if 'logged_in' not in session: return redirect(url_for('login'))
    return render_template('reports.html')

@app.route('/about')
def about():
    if 'logged_in' not in session: return redirect(url_for('login'))
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

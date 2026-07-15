from flask import Blueprint, jsonify, request, session
from utils.aws_client import get_aws_client, get_aws_resource
from utils.logger import log_activity
from config import Config

s3_bp = Blueprint('s3', __name__)

def get_user():
    return session.get('username', 'System')

@s3_bp.route('/list', methods=['GET'])
def list_buckets():
    s3 = get_aws_client('s3')
    if not s3: return jsonify({'error': 'Failed to connect to S3'}), 500
    
    try:
        response = s3.list_buckets()
        buckets = []
        for bucket in response['Buckets']:
            name = bucket['Name']
            creation_date = bucket['CreationDate'].strftime("%Y-%m-%d %H:%M:%S")
            buckets.append({
                'name': name,
                'creation_date': creation_date,
                # Note: Region and exact size/count requires more API calls, keeping it light for list view
                'region': s3.get_bucket_location(Bucket=name).get('LocationConstraint') or Config.AWS_REGION
            })
        return jsonify(buckets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@s3_bp.route('/create', methods=['POST'])
def create_bucket():
    data = request.json
    bucket_name = data.get('bucket_name')
    region = data.get('region', Config.AWS_REGION)
    s3 = get_aws_client('s3')
    
    try:
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        log_activity(get_user(), 'S3', f'Created bucket {bucket_name}', 'Success')
        return jsonify({'message': f'Bucket {bucket_name} created successfully'})
    except Exception as e:
        log_activity(get_user(), 'S3', f'Create bucket failed for {bucket_name}', f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@s3_bp.route('/delete', methods=['DELETE'])
def delete_bucket():
    bucket_name = request.json.get('bucket_name')
    s3 = get_aws_client('s3')
    
    try:
        s3.delete_bucket(Bucket=bucket_name)
        log_activity(get_user(), 'S3', f'Deleted bucket {bucket_name}', 'Success')
        return jsonify({'message': f'Bucket {bucket_name} deleted successfully'})
    except Exception as e:
        log_activity(get_user(), 'S3', f'Delete bucket failed for {bucket_name}', f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500
        
@s3_bp.route('/files', methods=['GET'])
def list_files():
    bucket_name = request.args.get('bucket')
    s3 = get_aws_client('s3')
    
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S")
                })
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@s3_bp.route('/upload', methods=['POST'])
def upload_file():
    bucket_name = request.form.get('bucket_name')
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    s3 = get_aws_client('s3')
    if not s3: return jsonify({'error': 'Failed to connect to S3'}), 500

    try:
        s3.upload_fileobj(file, bucket_name, file.filename)
        log_activity(get_user(), 'S3', f'Uploaded {file.filename} to {bucket_name}', 'Success')
        return jsonify({'message': f'File {file.filename} uploaded successfully'})
    except Exception as e:
        log_activity(get_user(), 'S3', f'Upload failed for {file.filename}', f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@s3_bp.route('/download_file', methods=['GET'])
def download_file():
    bucket_name = request.args.get('bucket')
    key = request.args.get('key')
    s3 = get_aws_client('s3')
    
    try:
        url = s3.generate_presigned_url('get_object',
                                        Params={'Bucket': bucket_name, 'Key': key},
                                        ExpiresIn=3600)
        log_activity(get_user(), 'S3', f'Downloaded file {key} from {bucket_name}', 'Success')
        return jsonify({'url': url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@s3_bp.route('/delete_file', methods=['DELETE'])
def delete_file():
    bucket_name = request.json.get('bucket')
    key = request.json.get('key')
    s3 = get_aws_client('s3')
    
    try:
        s3.delete_object(Bucket=bucket_name, Key=key)
        log_activity(get_user(), 'S3', f'Deleted file {key} from {bucket_name}', 'Success')
        return jsonify({'message': f'File {key} deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

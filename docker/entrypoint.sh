#!/bin/bash

set -e

# 1. Database migrations and data loading
echo "[Migrations] Running migrations..."
python citizens_project/manage.py migrate --noinput

echo "[Comorbidities] Checking comorbidities..."
python citizens_project/manage.py load_comorbidities

# 2. Automatically create the superuser if environment variables are set
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && "$DJANGO_SUPERUSER_USERNAME" != "admin" ]]; then
  echo "[Auth] Checking SuperUser..."
  python citizens_project/manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="$DJANGO_SUPERUSER_USERNAME").exists():
  User.objects.create_superuser(
    username="$DJANGO_SUPERUSER_USERNAME",
    email="$DJANGO_SUPERUSER_EMAIL",
    password="$DJANGO_SUPERUSER_PASSWORD"
  )
  print("Superuser created successfully")
else:
  print("Superuser already exists.")
EOF
fi 

# 3. Initialize S3 bucket
# Infrastructure healthchecks in docker-compose ensure S3 is ready.
if [[ -n "$AWS_S3_ENDPOINT_URL" && -n "$AWS_STORAGE_BUCKET_NAME" ]]; then
  echo "[S3] Initializing bucket: $AWS_STORAGE_BUCKET_NAME..."
  python -c "
import boto3, os, sys
from botocore.exceptions import ClientError

s3 = boto3.client('s3', 
    endpoint_url=os.environ.get('AWS_S3_ENDPOINT_URL'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
)
bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')

try:
    kwargs = {'Bucket': bucket}
    region = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    if region != 'us-east-1':
        kwargs['CreateBucketConfiguration'] = {'LocationConstraint': region}
    s3.create_bucket(**kwargs)
    print(f'Bucket {bucket} created successfully.')
except ClientError as e:
    error_code = e.response.get('Error', {}).get('Code')
    if error_code in ('BucketAlreadyExists', 'BucketAlreadyOwnedByYou'):
        print(f'Bucket {bucket} already exists.')
    else:
        print(f'Error initializing S3: {e}')
except Exception as e:
    print(f'Unexpected error during S3 init: {e}')
"
fi

# 4. Start Server
echo "[Server] Starting Django server..."
echo "Access the server at: http://localhost:8000"
python citizens_project/manage.py runserver 0.0.0.0:8000

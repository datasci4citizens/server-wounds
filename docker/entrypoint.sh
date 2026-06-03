#!/bin/bash

set -e

# 1. Initialize S3 bucket if environment variables are set
# We do this FIRST because it might need retries while other services boot up.
# We also reduce the wait time to make it feel faster.
if [[ -n "$AWS_S3_ENDPOINT_URL" && -n "$AWS_STORAGE_BUCKET_NAME" ]]; then
  echo "🪣 Initializing S3 bucket: $AWS_STORAGE_BUCKET_NAME..."
  python -c "
import boto3, os, time, sys
from botocore.exceptions import ClientError

s3 = boto3.client('s3', 
    endpoint_url=os.environ.get('AWS_S3_ENDPOINT_URL'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
)
bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')

max_retries = 10
for attempt in range(max_retries):
    try:
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
                raise e
        sys.exit(0)
    except Exception as e:
        print(f'Attempt {attempt + 1}/{max_retries} - S3 not ready yet, retrying...')
        if attempt < max_retries - 1:
            time.sleep(2) # Shorter wait for faster perceived boot
        else:
            print('Warning: S3 initialization failed. Continuing anyway...')
"
fi

# 2. Database migrations and data loading
echo "🔄 Running migrations..."
python citizens_project/manage.py migrate --noinput

echo "🧬 Checking comorbidities..."
python citizens_project/manage.py load_comorbidities

# 3. Automatically create the superuser if .env values are configured
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && "$DJANGO_SUPERUSER_USERNAME" != "admin" && \
     -n "$DJANGO_SUPERUSER_EMAIL" && "$DJANGO_SUPERUSER_EMAIL" != "admin@example.com" && \
     -n "$DJANGO_SUPERUSER_PASSWORD" && "$DJANGO_SUPERUSER_PASSWORD" != "admin" ]]; then

  echo "👤 Checking SuperUser..."
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

# 4. Start Server
echo "🚀 Starting Django server..."
echo "Access the server at: http://localhost:8000"
python citizens_project/manage.py runserver 0.0.0.0:8000

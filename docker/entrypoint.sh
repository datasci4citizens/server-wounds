#!/bin/bash

set -e

python citizens_project/manage.py migrate --noinput
python citizens_project/manage.py load_comorbidities

# Automatically create the superuser if .env values are configured
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && "$DJANGO_SUPERUSER_USERNAME" != "admin" && \
     -n "$DJANGO_SUPERUSER_EMAIL" && "$DJANGO_SUPERUSER_EMAIL" != "admin@example.com" && \
     -n "$DJANGO_SUPERUSER_PASSWORD" && "$DJANGO_SUPERUSER_PASSWORD" != "admin" ]]; then

  echo "👤 Creating SuperUser..."
  python citizens_project/manage.py shell <<EOF


from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="$DJANGO_SUPERUSER_USERNAME").exists(): # user does not exist
  User.objects.create_superuser(
    username="$DJANGO_SUPERUSER_USERNAME",
    email="$DJANGO_SUPERUSER_EMAIL",
    password="$DJANGO_SUPERUSER_PASSWORD"
  )
  print("Superuser created successfully")

  print("Access at: http://0.0.0.0:8000/admin" )
else:
  print("Superuser already exists, continuing initialization...")
EOF
else
    echo "Superuser environment variables are not defined."
fi 

echo "Starting Django server..."

# Initialize S3 bucket if environment variables are set
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

max_retries = 5
for attempt in range(max_retries):
    try:
        try:
            s3.create_bucket(Bucket=bucket)
            print(f'Bucket {bucket} created successfully.')
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code in ('BucketAlreadyExists', 'BucketAlreadyOwnedByYou'):
                print(f'Bucket {bucket} already exists.')
            else:
                raise e
        sys.exit(0)
    except Exception as e:
        print(f'Attempt {attempt + 1}/{max_retries} - Could not initialize bucket: {e}')
        if attempt < max_retries - 1:
            time.sleep(2)
        else:
            print('Failed to initialize bucket after maximum retries.')
            # We don't exit 1 here to allow the server to start even if init failed 
            # (it might be a transient network issue during startup)
"
fi

echo "Access the server at: http://localhost:8000"
python citizens_project/manage.py runserver 0.0.0.0:8000

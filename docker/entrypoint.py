import os
import subprocess
import sys
from pathlib import Path
from botocore.exceptions import ClientError
import boto3

DEFAULT_SUPERUSER_USERNAME = "admin"
DEFAULT_SUPERUSER_PASSWORD = "admin"
ROOT_DIR = Path(__file__).resolve().parent.parent
MANAGE = ROOT_DIR / "citizens_project" / "manage.py"


def run_command(command):
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)


def init_s3_bucket():
    endpoint_url = os.environ.get("AWS_S3_ENDPOINT_URL")
    bucket_name = os.environ.get("AWS_STORAGE_BUCKET_NAME")

    if not endpoint_url or not bucket_name:
        return

    print(f"[S3] Initializing bucket: {bucket_name}...")
    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_S3_REGION_NAME", "us-east-1"),
    )

    try:
        kwargs = {"Bucket": bucket_name}
        region_name = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
        if region_name != "us-east-1":
            kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region_name}

        s3.create_bucket(**kwargs)
        print(f"Bucket {bucket_name} created successfully.")
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code in ("BucketAlreadyExists", "BucketAlreadyOwnedByYou"):
            print(f"Bucket {bucket_name} already exists.")
        else:
            print(f"Error initializing S3: {e}")
    except Exception as e:
        print(f"Unexpected error during S3 init: {e}")


def main():
    print("Starting entrypoint...")

    print("Applying migrations...")

    run_command(["python", str(MANAGE), "migrate", "--noinput"])

    print("Loading Comorbidities")
    run_command(["python", str(MANAGE), "load_comorbidities"])

    print("Collecting static files...")
    # run_command(["python", manage, "collectstatic", "--noinput"])

    superuser_username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    superuser_password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    if (
        superuser_username
        and superuser_password
        and superuser_username != DEFAULT_SUPERUSER_USERNAME
        and superuser_password != DEFAULT_SUPERUSER_PASSWORD
    ):
        print("Checking/Creating superuser...")
        try:
            subprocess.run(["python", str(MANAGE), "createsuperuser", "--noinput"], check=True)
            print("Superuser process finished.")
        except subprocess.CalledProcessError:
            pass

    init_s3_bucket()

    if len(sys.argv) > 1:
        print(f"Executing: {' '.join(sys.argv[1:])}")
        os.execvp(sys.argv[1], sys.argv[1:])

    run_command(["python", str(MANAGE), "runserver", "0.0.0.0:8000"])


if __name__ == "__main__":
    main()
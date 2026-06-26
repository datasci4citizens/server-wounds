import os
import sys
import subprocess
from pathlib import Path

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


def main():
    print("Starting entrypoint...")

    print("Applying migrations...")

    run_command(["python", str(MANAGE), "migrate", "--noinput"])

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

    if len(sys.argv) > 1:
        print(f"Executing: {' '.join(sys.argv[1:])}")
        os.execvp(sys.argv[1], sys.argv[1:])

    run_command(["python", str(MANAGE), "runserver", "0.0.0.0:8000"])


if __name__ == "__main__":
    main()
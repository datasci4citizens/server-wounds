import os
import sys
import subprocess

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
    run_command(["python", "manage.py", "migrate", "--noinput"])

    print("Collecting static files...")
    run_command(["python", "manage.py", "collectstatic", "--noinput"])

    superuser_username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    superuser_password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    if superuser_username and superuser_password:
        print("Checking/Creating superuser...")
        create_script = (
            f"import os; "
            f"from django.contrib.auth import get_user_model; "
            f"User = get_user_model(); "
            f"exists = User.objects.filter(username='{superuser_username}').exists(); "
            f"print('User exists:', exists); "
            f"not exists and User.objects.create_superuser('{superuser_username}', os.environ.get('DJANGO_SUPERUSER_EMAIL', ''), '{superuser_password}')"
        )
        try:
            subprocess.run(["python", "manage.py", "shell", "-c", create_script], check=True)
            print("Superuser process finished.")
        except subprocess.CalledProcessError:
            print("Failed to handle superuser creation, but moving forward.")
    else:
        print("Superuser config missing. Skipping.")

    if len(sys.argv) > 1:
        print(f"Executing: {' '.join(sys.argv[1:])}")
        os.execvp(sys.argv[1], sys.argv[1:])
    else:
        print("No command provided.")

if __name__ == "__main__":
    main()
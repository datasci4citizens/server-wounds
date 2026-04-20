import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "citizens_project.settings")
try:
    django.setup()
    print("Django setup successful!")
except Exception as e:
    import traceback
    traceback.print_exc()


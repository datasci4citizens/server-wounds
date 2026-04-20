import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "citizens_project.settings")
django.setup()

from app_cicatrizando.serializers import ProviderPatientRegisterSerializer

s = ProviderPatientRegisterSerializer(data={
    "name": "Test",
    "birth_date": "1990-01-01",
    "state": "SP",
    "city": "Sao Paulo",
    "contact_email": "test@test.com"
})
print("Is valid:", s.is_valid())
if not s.is_valid():
    print("Errors:", s.errors)

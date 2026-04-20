import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "citizens_project.settings")
django.setup()

from app_cicatrizando.models import Provider, Patient

for p in Provider.objects.all():
    print(f"Provider: {p.wounds_user.user.email} - Patients: {p.patient_set.all() if hasattr(p, 'patient_set') else p.patient_set.all() if hasattr(p, 'patient_set') else '???'}")
    patients = Patient.objects.filter(Specialist=p)
    print(f"  Patients from Patient.objects.filter(Specialist=p): {patients}")
    for pat in patients:
        print(f"    - {pat.wounds_user.user.email} ({pat.wounds_user.name})")

print("All Patients:")
for pat in Patient.objects.all():
    print(f"Patient: {pat.wounds_user.user.email} - Specialists: {pat.Specialist.all()}")


from django.db import models
from django.contrib.auth import get_user_model

django_user = get_user_model()

class Comorbidity(models.Model):
    name = models.CharField(max_length=255)
    concept_id = models.CharField(max_length=255, primary_key=True)

class WoundsUser(models.Model):
    user = models.OneToOneField(django_user, on_delete=models.CASCADE, related_name="wounds_user")
    
    birth_date = models.DateField(blank=True, null=True)
    state = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    Provider = "Pr"
    Patient = "Pa"
    roles = [
        (Patient, "Paciente"),
        (Provider, "Especialista"),
    ]
    role = models.CharField(choices=roles, max_length=2, blank=True)
    
class Provider(models.Model):
    wounds_user = models.OneToOneField(WoundsUser, on_delete=models.CASCADE, related_name="provider")

    professional_id = models.CharField(max_length=15, unique=True)
    contact_email = models.EmailField(blank=True, null=True, max_length=50, unique = True)
    contact_phone = models.CharField(blank=True, null=True, max_length=15, unique = True) 

class Patient(models.Model):
    wounds_user = models.OneToOneField(WoundsUser, on_delete=models.CASCADE)
    
    contact_email = models.EmailField(blank=True, null=True, max_length=50, unique = True)
    contact_phone = models.CharField(blank=True, null=True, max_length=15, unique = True) 

    assigned_providers = models.ManyToManyField(Provider)
    comorbidities = models.ManyToManyField(Comorbidity)
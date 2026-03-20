from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()





class WoundsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wounds_user")
    
    birth_date = models.DateField(blank=True)
    state = models.CharField(blank=True)
    city = models.CharField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    Provider = "Pr"
    Patient = "Pa"
    roles = [
        (Patient, "Paciente"),
        (Provider, "Especialista"),
    ]
    role = models.CharField(choices=roles, max_length=2, default=Patient)
    

class Provider(models.Model):
    wounds_user = models.OneToOneField(User, on_delete=models.CASCADE)

    Professional_ID = models.PositiveIntegerField()
    contact_email = models.EmailField(blank=True)
    contact_number = models.CharField(blank=True, max_length=11,) 

class Patient(models.Model):
    WoundsUser = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_email = models.EmailField(blank=True)
    contact_numer = models.CharField(blank=True)
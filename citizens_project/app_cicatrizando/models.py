from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WoundsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wounds_user")
    
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

    professional_document = models.CharField(max_length=30)
    professional_id = models.CharField(max_length=50)
    contact_email = models.EmailField(blank=True, null=True, max_length=50, unique = true)
    contact_phone = models.CharField(blank=True, null=True max_length=15, unique = true) 


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["professional_document", "professional_id"], name="unique_provider"
            )
        ]


class Patient(models.Model):
    wounds_user = models.OneToOneField(WoundsUser, on_delete=models.CASCADE)
    
    contact_email = models.EmailField(blank=True, null=True, max_length=50, unique = true)
    contact_phone = models.CharField(blank=True, null=True max_length=15, unique = true) 

    assigned_providers = models.ManyToManyField(Provider)
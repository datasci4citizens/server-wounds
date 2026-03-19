from django.db import models
from django.contrib.auth import get_user_model
# from .omop.omop_models import Person, Provider

User = get_user_model()


class WoundsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wounds_user")
    
    name = models.CharField(max_length=255)
    birth_date = models.DateField()
    email = models.EmailField()
    

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
    wounds_user = models.OneToOneField(
        WoundsUser,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="id",
        related_name="provider",
    )



#     class PatientNonClinicalInfos(models.Model):
#         # person = models.ForeignKey(Person, models.DO_NOTHING)
#         name = models.CharField(max_length=255)
#         # phone_number = models.CharField(max_length=20, null=True, blank=True)
#         # accept_tcl = models.BooleanField(default=False)
#         created_at = models.DateTimeField(auto_now_add=True)
#         bind_code  = models.IntegerField(unique=True, null=True)
#         user  = models.ForeignKey(User, models.SET_NULL, null=True)
#         updated_at = models.DateTimeField(auto_now=True)


#    class ProviderNonClinicalInfos(models.Model):
#        provider = models.ForeignKey(Provider, models.DO_NOTHING)
#        name = models.CharField(max_length=255, null=True, blank=True)
#        phone_number = models.CharField(max_length=20, null=True, blank=True)
#        user = models.ForeignKey(User, models.SET_NULL, null=True)
#        created_at = models.DateTimeField(auto_now_a#dd=True)
#        updated_at = models.DateTimeField(auto_now=True)

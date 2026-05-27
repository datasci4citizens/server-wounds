from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

class GenderChoices(models.TextChoices):
    MALE = 'M', 'Masculino'
    FEMALE = 'F', 'Feminino'

class SmokingChoices(models.TextChoices):
    NEVER = 'NEVER', 'Nunca fumou'
    LT10 = 'LT10', 'Menos de 10 cigarros por dia'
    GT10 = 'GT10', 'Mais de 10 cigarros por dia'
    EX = 'EX', 'Ex-tabagista'

class AlcoholChoices(models.TextChoices):
    NONE = 'NONE', 'Não bebe'
    EX = 'EX', 'Ex-etilista'
    LT21_M = 'LT21_M', 'Menos de 21 doses por semana (H)'
    GT21_M = 'GT21_M', 'Mais de 21 doses por semana (H)'
    LT13_M = 'LT13_M', 'Menos de 13 latas por semana (H)'
    GT13_M = 'GT13_M', 'Mais de 13 latas por semana (H)'
    LT14_F = 'LT14_F', 'Menos de 14 doses por semana (M)'
    GT14_F = 'GT14_F', 'Mais de 14 doses por semana (M)'
    LT9_F = 'LT9_F', 'Menos de 9 latas por semana (M)'
    GT9_F = 'GT9_F', 'Mais de 9 latas por semana (M)'


django_user = get_user_model()

class Comorbidity(models.Model):
    name = models.CharField(max_length=255)
    concept_id = models.CharField(max_length=255, primary_key=True)
    code = models.CharField(max_length=50, blank=True, null=True)

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

    gender = models.CharField(max_length=1, choices=GenderChoices.choices, blank=True, null=True)
    height = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0.0), MaxValueValidator(3.0)], blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.0), MaxValueValidator(500.0)], blank=True, null=True)
    smoking_status = models.CharField(max_length=10, choices=SmokingChoices.choices, blank=True, null=True)
    alcohol_consumption = models.CharField(max_length=10, choices=AlcoholChoices.choices, blank=True, null=True)

    assigned_providers = models.ManyToManyField(Provider)
    comorbidities = models.ManyToManyField(Comorbidity)
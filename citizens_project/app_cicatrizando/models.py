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

class WoundEtiology(models.TextChoices):
    DIABETIC_FOOT = 'Úlcera do pé diabético', 'Úlcera do pé diabético'
    PRESSURE_INJURY = 'Lesão por pressão', 'Lesão por pressão'
    VENOUS_ULCER = 'Úlcera venosa', 'Úlcera venosa'
    ARTERIAL_ULCER = 'Úlcera arterial', 'Úlcera arterial'
    TRAUMA = 'Ferida por trauma', 'Ferida por trauma'
    SURGICAL = 'Ferida cirúrgica', 'Ferida cirúrgica'
    BURN = 'Queimadura', 'Queimadura'
    SKIN_TEAR = 'Skin tear', 'Skin tear'
    FISTULA = 'Fístula', 'Fístula'
    NEOPLASTIC = 'Ferida neoplásica', 'Ferida neoplásica'
    PHLEBITIS = 'Flebite', 'Flebite'

class WoundLocation(models.TextChoices):
    KNEE_ANTERIOR = 'Anterior do joelho', 'Anterior do joelho'
    KNEE_POSTERIOR = 'Posterior do joelho', 'Posterior do joelho'
    BELOW_KNEE_POSTERIOR = 'Abaixo do joelho, região posterior', 'Abaixo do joelho, região posterior'
    BELOW_KNEE_ANTERIOR = 'Abaixo do joelho, região anterior', 'Abaixo do joelho, região anterior'
    ABOVE_MEDIAL_MALLEOLUS = 'Acima do maleolo medial', 'Acima do maleolo medial'
    BELOW_MEDIAL_MALLEOLUS = 'Abaixo do maleolo medial', 'Abaixo do maleolo medial'
    ABOVE_LATERAL_MALLEOLUS = 'Acima do maleolo lateral', 'Acima do maleolo lateral'
    BELOW_LATERAL_MALLEOLUS = 'Abaixo do maleolo lateral', 'Abaixo do maleolo lateral'
    CALCANEAL = 'Região calcaneana', 'Região calcaneana'
    FOOT_DORSUM = 'Dorso do pé', 'Dorso do pé'
    FOOT_PLANTAR = 'Planta do pé', 'Planta do pé'
    HALLUX = 'Halux', 'Halux'
    SECOND_TOE = '2ª Pododáctilo', '2ª Pododáctilo'
    THIRD_TOE = '3ª Pododáctilo', '3ª Pododáctilo'
    FOURTH_TOE = '4ª Pododáctilo', '4ª Pododáctilo'
    FIFTH_TOE = '5ª Pododáctilo', '5ª Pododáctilo'

class ExudateAmount(models.TextChoices):
    NONE = 'Nenhum', 'Nenhum'
    LOW = 'Pouco', 'Pouco'
    MODERATE = 'Médio', 'Médio'
    HIGH = 'Muito', 'Muito'

class ExudateType(models.TextChoices):
    SEROUS = 'Seroso', 'Seroso'
    PURULENT = 'Purulento', 'Purulento'
    SANGUINEOUS = 'Sanguinolento', 'Sanguinolento'
    SEROSANGUINEOUS = 'Serosanguinolento', 'Serosanguinolento'
    ABSENT = 'Ausente', 'Ausente'

class TissueType(models.TextChoices):
    HEALED = 'Cicatrizado', 'Cicatrizado'
    EPITHELIALIZATION = 'Epitelização', 'Epitelização'
    GRANULATION = 'Granulação', 'Granulação'
    DEVITALIZED = 'Desvitalizado', 'Desvitalizado'
    NECROTIC = 'Necrótico', 'Necrótico'

class PeriwoundSkinStatus(models.TextChoices):
    EDEMA = 'Inchaço/Edema', 'Inchaço/Edema'
    ERYTHEMA_LT_2CM = 'Eritema menor que 2 cm', 'Eritema menor que 2 cm'
    ERYTHEMA_GT_2CM = 'Eritema maior que 2 cm', 'Eritema maior que 2 cm'

class WoundEdgeStatus(models.TextChoices):
    UNDEFINED = 'Indefinidas, não visíveis claramente', 'Indefinidas, não visíveis claramente'
    DEFINED_ADHERED = 'Definidas, contorno claramente visível, aderidas, niveladas com a base da ferida', 'Definidas, contorno claramente visível, aderidas, niveladas com a base da ferida'
    DEFINED_NOT_ADHERED = 'Bem definidas, não aderidas à base da ferida', 'Bem definidas, não aderidas à base da ferida'
    DEFINED_ROLLED = 'Bem definidas, não aderidas à base, enrolada, espessada', 'Bem definidas, não aderidas à base, enrolada, espessada'
    DEFINED_FIBROTIC = 'Bem definidas, fibróticas, com crostas e/ou hiperqueratose.', 'Bem definidas, fibróticas, com crostas e/ou hiperqueratose.'

class Wound(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="wounds")
    etiology = models.CharField(max_length=50, choices=WoundEtiology.choices)
    location = models.CharField(max_length=100, choices=WoundLocation.choices)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_healed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.etiology} - {self.location} ({self.patient.wounds_user.user.get_full_name()})"

class Observation(models.Model):
    wound = models.ForeignKey(Wound, on_delete=models.CASCADE, related_name="observations")
    author = models.ForeignKey(WoundsUser, on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Clinical Metrics
    pain_level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    exudate_amount = models.CharField(max_length=20, choices=ExudateAmount.choices)
    exudate_type = models.CharField(max_length=20, choices=ExudateType.choices)
    tissue_type = models.CharField(max_length=20, choices=TissueType.choices)
    dressing_changes = models.IntegerField()
    periwound_skin = models.CharField(max_length=50, choices=PeriwoundSkinStatus.choices)
    wound_edge = models.CharField(max_length=255, choices=WoundEdgeStatus.choices)
    fever_24h = models.BooleanField(default=False)
    
    # Notes
    extra_notes = models.TextField(blank=True, null=True)
    patient_guidelines = models.TextField(blank=True, null=True)
    
    # Media (Phase 4 - will be added later)
    # image = models.ImageField(upload_to='wounds/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Observation {self.created_at} for {self.wound}"
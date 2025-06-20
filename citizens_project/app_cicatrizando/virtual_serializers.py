from datetime import date
from django.core.validators import RegexValidator
from .omop.omop_models import (
    Concept,
    Observation,
    Provider
)
from .omop import omop_ids
from .models import (
    Image
)
from .django_virtualmodels.models import (
    all_attr_ofclass
)
from .django_virtualmodels.serializers import VirtualModelSerializer
from .virtual_models import (VirtualSpecialist, VirtualWound, VirtualTrackingRecords, VirtualPatient, VirtualComorbidity)
from . import virtual_models
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from datetime import datetime
import random
User = get_user_model()

for const_name in all_attr_ofclass(omop_ids, int):
    try:
        Concept.objects.get_or_create(
            concept_id=  getattr(omop_ids, const_name),
            concept_name= const_name
        )
    except:
        pass
# serializers.py
from rest_framework import serializers
from datetime import datetime

class TimezoneAwareDateField(serializers.DateField):
    def to_internal_value(self, value):
        try:
            # Converte a string ISO para datetime (considera UTC se terminado com 'Z')
            parsed_date = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
            # Extrai apenas a parte da data (ignora horário e fuso)
            return parsed_date.date()
        except (ValueError, TypeError):
            # Se falhar, tenta o formato padrão do DRF (YYYY-MM-DD)
            return super().to_internal_value(value)
        
class VirtualSpecialistSerializer(serializers.Serializer):
    specialist_id   = serializers.IntegerField(read_only=True)
    specialist_name = serializers.CharField(max_length = 255)
    email           = serializers.EmailField(max_length = 255)
    birthday        = TimezoneAwareDateField(allow_null=True, required=False)
    speciality      = serializers.CharField(max_length=40, allow_null=True, required=False)
    city            = serializers.CharField(allow_null=True, required=False, max_length = 100)
    state           = serializers.CharField(allow_null=True, required=False, max_length = 100)

    def validate_email(self, value):
        # valida se o email ja nao esta em uso
        try:
            if Provider.objects.filter(provider_user__email = value):
                raise serializers.ValidationError("Este e-mail já está em uso.")
        except User.DoesNotExist:
            pass 
        return value
    

    
    def validate_birthday(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data de nascimento não pode ser no futuro.")
        return value

    @transaction.atomic()
    def create(self, validated_data):
        
        user, _ = User.objects.get_or_create(
            username=validated_data["email"],
            email=validated_data["email"]
        )
        validated_data = VirtualSpecialist.create({
            "specialist_name": validated_data["specialist_name"],
            "user_id": user.id,
            "birthday": validated_data["birthday"],
            "speciality": validated_data["speciality"],
            "city": validated_data["city"],
            "state": validated_data["state"],
        })
        
        return {
            "specialist_id": validated_data["specialist_id"], 
            "specialist_name": validated_data["specialist_name"], 
            "email": user.email, 
            "birthday": validated_data["birthday"], 
            "speciality": validated_data["speciality"],
            "city": validated_data["city"],
            "state": validated_data["state"] 
        }

    def update(self, instance, validated_data : dict[str, object]):

        validated_data["specialist_id"] =  instance["provider_id"]
        updatable_fields = [
            "specialist_name",
            "birthday",
            "speciality",
            "city",
            "state"
        ]
        validated_data = VirtualSpecialist.update({
            field : validated_data[field]
            for field in updatable_fields
            if field in validated_data.keys()
        })
        return VirtualSpecialist.get(**validated_data)
    
class VirtualPatientSerializer(serializers.Serializer):
    patient_id            = serializers.IntegerField(read_only=True)
    name                  = serializers.CharField(max_length = 255)
    gender                = serializers.ChoiceField(choices=virtual_models.map_gender.virtual_values())
    birthday              = TimezoneAwareDateField()
    specialist_id         = serializers.IntegerField(required=False)
    hospital_registration = serializers.CharField(allow_null=True, required=False, max_length = 255)

    phone_regex = RegexValidator(
        regex = r'^\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}$',
        message = "O número de telefone deve estar no formato: (XX) XXXX-XXXX ou (XX) XXXXX-XXXX."
    )
    phone_number          = serializers.CharField(allow_null=True, required=False, max_length = 20, validators = [phone_regex])
    weight                = serializers.FloatField(allow_null=True, required=False)
    height                = serializers.FloatField(allow_null=True, required=False)
    accept_tcl            = serializers.BooleanField(required=False)
    smoke_frequency       = serializers.ChoiceField(allow_null=True, required=False, choices=virtual_models.map_smoke_frequency.virtual_values())
    drink_frequency       = serializers.ChoiceField(allow_null=True, required=False, choices=virtual_models.map_drink_frequency.virtual_values())

    email                 = serializers.EmailField(read_only=True)
    comorbidities         = serializers.ListField(child=serializers.ChoiceField(choices=virtual_models.map_comorbidities.virtual_values()), allow_empty= True)
    bind_code             = serializers.IntegerField(read_only=True)

    def validate_birthday(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data de nascimento não pode ser no futuro.")
        return value
    
    def validate_weight(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("O peso deve ser um valor positivo.")
        return value

    def validate_height(self, value):
        # Validação para garantir que a altura é positiva
        if value is not None and value <= 0:
            raise serializers.ValidationError("A altura deve ser um valor positivo.")
        return value
    

    
    def validate_accept_tcl(self, value):
        if self.context.get('request') and self.context['request'].method == 'POST':
            if not value:
                raise serializers.ValidationError("É necessário aceitar os Termos e Condições de Uso para participar da pesquisa.")
        return value
 
    @transaction.atomic()
    def create(self, validated_data):
        virtual_patient_fields  = [
            "name",
            "gender",
            "birthday",
            "specialist_id",
            "phone_number",
            "weight",
            "height",
            "accept_tcl",
            "smoke_frequency",
            "drink_frequency",
            "hospital_registration"
        ]
        data = {
            field: validated_data[field]
            for field in virtual_patient_fields
        }
        data["updated_at"] = datetime.now()
        data["bind_code"] = random.randrange(0, 1048576) 
        result = VirtualPatient.create(data)
        
        for c in set(validated_data["comorbidities"]):
            obs = Observation.objects.create(
                person_id = result["patient_id"],
                observation_concept_id =  omop_ids.CID_COMORBIDITY,
                observation_type_concept_id = omop_ids.CID_EHR,
                value_as_concept_id = virtual_models.map_comorbidities.virtual_to_db(c),
                observation_date = data["updated_at"]
            )
        
        return result
    def validate_gender(self, value):
        result = VirtualPatient.descriptor().fields["gender"].validate(value)
        if result != None:
            raise serializers.ValidationError(result)
        return value

class VirtualWoundSerializer(serializers.Serializer):
    wound_id      = serializers.IntegerField(read_only=True) 
    patient_id    = serializers.IntegerField(required=True) 
    specialist_id = serializers.IntegerField(required=True) 
    updated_at    = serializers.DateTimeField(read_only=True)
    region        = serializers.ChoiceField(required=True, choices=virtual_models.map_wound_location.virtual_values())     
    wound_type    = serializers.ChoiceField(required=True, choices=virtual_models.map_wound_type.virtual_values()) 
    start_date    = TimezoneAwareDateField(required=True) 
    end_date      = TimezoneAwareDateField(allow_null=True, required=False)
    is_active     = serializers.BooleanField(required=True)
    image_url     = serializers.URLField(read_only=True)


    def _validate_concept_id_existence(self, value, field_name):
        if value:
            try:
                Concept.objects.get(concept_id=value)
            except Concept.DoesNotExist:
                raise serializers.ValidationError(
                    f"O Concept ID '{value}' para '{field_name}' não foi encontrado na base de conceitos OMOP."
                )
        return value

    def validate_start_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data de início da ferida não pode ser no futuro.")
        return value

    def validate_end_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data de término da ferida não pode ser no futuro.")
        return value
    

    
class ImageSerializer(serializers.ModelSerializer):
    def validate_image(self, value):
        if not value.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            raise serializers.ValidationError("O arquivo deve ser uma imagem (PNG, JPG, JPEG, GIF).")
        return value
    class Meta:
        model = Image
        fields = ['image']

class VirtualTrackingRecordsSerializer(serializers.Serializer):
    tracking_id              = serializers.IntegerField(read_only=True)
    patient_id               = serializers.IntegerField(required=True)
    specialist_id            = serializers.IntegerField(required=True)
    wound_id                 = serializers.IntegerField(required=True)
    track_date               = serializers.DateField(read_only=True)
    length                   = serializers.FloatField(min_value=0.0, allow_null=True, required=False)
    width                    = serializers.FloatField(min_value=0.0, allow_null=True, required=False)
    exudate_amount           = serializers.ChoiceField(allow_null=True, required=True, choices=virtual_models.map_exudate_amount.virtual_values()) 
    exudate_type             = serializers.ChoiceField(allow_null=True, required=True, choices=virtual_models.map_exudate_type.virtual_values())    
    tissue_type              = serializers.ChoiceField(allow_null=True, required=True, choices=virtual_models.map_tissue_type.virtual_values())
    wound_edges              = serializers.ChoiceField(allow_null=True, required=True, choices=virtual_models.map_wound_edges.virtual_values())
    skin_around              = serializers.ChoiceField(allow_null=True, required=True, choices=virtual_models.map_skin_around.virtual_values())
    had_a_fever              = serializers.BooleanField(required=False)
    pain_level               = serializers.IntegerField(min_value=0, max_value=10, allow_null=True, required=False)
    dressing_changes_per_day = serializers.IntegerField(min_value=0, allow_null=True, required=False) 
    guidelines_to_patient    = serializers.CharField(max_length=1000, allow_null=True, required=False)
    extra_notes              = serializers.CharField(max_length=1000, allow_null=True, required=False)
    image_url                = serializers.URLField(read_only=True)
    
    def _validate_concept_id_existence(self, value, field_name):
        if value:
            try:
                Concept.objects.get(concept_id=value)
            except Concept.DoesNotExist:
                raise serializers.ValidationError(
                    f"O Concept ID '{value}' para '{field_name}' não foi encontrado na base de conceitos OMOP."
                )
        return value

    def validate_track_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data do acompanhamento não pode ser no futuro.")
        return value
        
class VirtualComorbiditySerializer(VirtualModelSerializer):
    comorbidity_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        super_model = VirtualComorbidity
        model = VirtualComorbidity
        fields = "__all__"
        read_only_fields = ["comorbidity_id", "comorbidity_name"]

    def validate_comorbidity_type(self, value):
        # Garante que o concept existe
        if not Concept.objects.filter(concept_id=value).exists():
            raise serializers.ValidationError(f"O conceito com ID {value} não existe. Certifique-se de que ele foi criado.")
        return value

    def get_comorbidity_name(self, obj):
        comorbidity_type = None
        if isinstance(obj, dict):
            comorbidity_type = obj.get('comorbidity_type')
        else:
            comorbidity_type = getattr(obj, 'comorbidity_type', None)
        if not comorbidity_type:
            return None
        concept = Concept.objects.filter(concept_id=comorbidity_type).first()
        return concept.concept_name if concept else None

    
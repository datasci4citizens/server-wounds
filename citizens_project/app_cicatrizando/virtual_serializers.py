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

# Este loop inicializa ou garante a existência de conceitos OMOP essenciais no banco de dados.
# Ele percorre todas as constantes inteiras definidas no módulo `omop_ids`.
for const_name in all_attr_ofclass(omop_ids, int):
    try:
        # Para cada constante, tenta obter ou criar um registro na tabela `Concept` do OMOP.
        # O `concept_id` é o valor da constante e o `concept_name` é o nome da constante.
        Concept.objects.get_or_create(
            concept_id=  getattr(omop_ids, const_name),
            concept_name= const_name
        )
    except:
        # Erros durante a criação/obtenção são ignorados.
        pass
# serializers.py
from rest_framework import serializers
from datetime import datetime

class TimezoneAwareDateField(serializers.DateField):
    # Converte um valor de data de entrada (que pode incluir fuso horário) para um objeto `date` simples.
    def to_internal_value(self, value):
        try:
            # Tenta analisar a string de data como um datetime ISO 8601 com fuso horário.
            parsed_date = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z')
            # Retorna apenas a parte da data, ignorando o tempo e o fuso horário.
            return parsed_date.date()
        except (ValueError, TypeError):
            # Se a análise com fuso horário falhar, tenta o comportamento padrão de `serializers.DateField`.
            return super().to_internal_value(value)
        
class VirtualSpecialistSerializer(serializers.Serializer):
    # Campo somente leitura para o ID do especialista.
    specialist_id   = serializers.IntegerField(read_only=True)
    # Campo para o nome do especialista, com tamanho máximo.
    specialist_name = serializers.CharField(max_length = 255)
    # Campo para o e-mail do especialista, com tamanho máximo.
    email           = serializers.EmailField(max_length = 255)
    # Campo opcional para a data de nascimento, usando o `TimezoneAwareDateField` personalizado.
    birthday        = TimezoneAwareDateField(allow_null=True, required=False)
    # Campo opcional para a especialidade, com tamanho máximo.
    speciality      = serializers.CharField(max_length=40, allow_null=True, required=False)
    # Campo opcional para a cidade, com tamanho máximo.
    city            = serializers.CharField(allow_null=True, required=False, max_length = 100)
    # Campo opcional para o estado, com tamanho máximo.
    state           = serializers.CharField(allow_null=True, required=False, max_length = 100)

    # Valida se o e-mail já está em uso por outro provedor.
    def validate_email(self, value):
        # valida se o email ja nao esta em uso
        try:
            if Provider.objects.filter(provider_user__email = value):
                raise serializers.ValidationError("Este e-mail já está em uso.")
        except User.DoesNotExist:
            pass 
        return value
    

    
    # Valida se a data de nascimento não é no futuro.
    def validate_birthday(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data de nascimento não pode ser no futuro.")
        return value

    # Cria um novo especialista. Usa uma transação atômica para garantir consistência.
    @transaction.atomic()
    def create(self, validated_data):
        
        # Obtém ou cria um objeto User para o especialista com o e-mail como username.
        user, _ = User.objects.get_or_create(
            username=validated_data["email"],
            email=validated_data["email"]
        )
        # Cria o especialista virtual usando os dados validados e o ID do usuário.
        validated_data = VirtualSpecialist.create({
            "specialist_name": validated_data["specialist_name"],
            "user_id": user.id,
            "birthday": validated_data["birthday"],
            "speciality": validated_data["speciality"],
            "city": validated_data["city"],
            "state": validated_data["state"],
        })
        
        # Retorna os dados do especialista criado, incluindo o e-mail do usuário.
        return {
            "specialist_id": validated_data["specialist_id"], 
            "specialist_name": validated_data["specialist_name"], 
            "email": user.email, 
            "birthday": validated_data["birthday"], 
            "speciality": validated_data["speciality"],
            "city": validated_data["city"],
            "state": validated_data["state"] 
        }

    # Atualiza um especialista existente.
    def update(self, instance, validated_data : dict[str, object]):

        # Define o ID do especialista a ser atualizado.
        validated_data["specialist_id"] =  instance["provider_id"]
        # Lista de campos que podem ser atualizados.
        updatable_fields = [
            "specialist_name",
            "birthday",
            "speciality",
            "city",
            "state"
        ]
        # Atualiza o especialista virtual com os campos fornecidos nos dados validados.
        validated_data = VirtualSpecialist.update({
            field : validated_data[field]
            for field in updatable_fields
            if field in validated_data.keys()
        })
        # Retorna a instância atualizada do especialista.
        return VirtualSpecialist.get(**validated_data)
    
class VirtualPatientSerializer(serializers.Serializer):
    # Campo somente leitura para o ID do paciente.
    patient_id            = serializers.IntegerField(read_only=True)
    # Campo para o nome do paciente.
    name                  = serializers.CharField(max_length = 255)
    # Campo para o gênero do paciente, usando choices mapeados de `virtual_models`.
    gender                = serializers.ChoiceField(choices=virtual_models.map_gender.virtual_values())
    # Campo para a data de nascimento do paciente.
    birthday              = TimezoneAwareDateField()
    # Campo opcional para o ID do especialista.
    specialist_id         = serializers.IntegerField(required=False)
    # Campo opcional para o registro hospitalar.
    hospital_registration = serializers.CharField(allow_null=True, required=False, max_length = 255)

    # Validador de expressão regular para o formato do número de telefone.
    phone_regex = RegexValidator(
        regex = r'^\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}$',
        message = "O número de telefone deve estar no formato: (XX) XXXX-XXXX ou (XX) XXXXX-XXXX."
    )
    # Campo opcional para o número de telefone, usando o validador definido acima.
    phone_number          = serializers.CharField(allow_null=True, required=False, max_length = 20, validators = [phone_regex])
    # Campo opcional para o peso.
    weight                = serializers.FloatField(allow_null=True, required=False)
    # Campo opcional para a altura.
    height                = serializers.FloatField(allow_null=True, required=False)
    # Campo opcional para o aceite dos termos e condições.
    accept_tcl            = serializers.BooleanField(required=False)
    # Campo opcional para a frequência de fumo, usando choices mapeados.
    smoke_frequency       = serializers.ChoiceField(allow_null=True, required=False, choices=virtual_models.map_smoke_frequency.virtual_values())
    # Campo opcional para a frequência de bebida, usando choices mapeados.
    drink_frequency       = serializers.ChoiceField(allow_null=True, required=False, choices=virtual_models.map_drink_frequency.virtual_values())

    # Campo somente leitura para o e-mail (provavelmente derivado do usuário associado).
    email                 = serializers.EmailField(read_only=True)
    # Campo para a lista de comorbidades, permitindo que seja vazia.
    comorbidities         = serializers.ListField(child=serializers.ChoiceField(choices=virtual_models.map_comorbidities.virtual_values()), allow_empty= True)
    # Campo somente leitura para o código de vínculo.
    bind_code             = serializers.IntegerField(read_only=True)

    # Valida se a data de nascimento não é no futuro.
    def validate_birthday(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data de nascimento não pode ser no futuro.")
        return value
    
    # Valida se o peso é um valor positivo.
    def validate_weight(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("O peso deve ser um valor positivo.")
        return value

    # Valida se a altura é um valor positivo.
    def validate_height(self, value):
        # Validação para garantir que a altura é positiva
        if value is not None and value <= 0:
            raise serializers.ValidationError("A altura deve ser um valor positivo.")
        return value
    

    
    # Valida o aceite dos termos e condições, especialmente na criação (POST).
    def validate_accept_tcl(self, value):
        if self.context.get('request') and self.context['request'].method == 'POST':
            if not value:
                raise serializers.ValidationError("É necessário aceitar os Termos e Condições de Uso para participar da pesquisa.")
        return value
 
    # Cria um novo paciente virtual e suas comorbidades associadas. Usa uma transação atômica.
    @transaction.atomic()
    def create(self, validated_data):
        # Lista de campos que serão usados para criar o `VirtualPatient`.
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
        # Constrói o dicionário de dados para a criação do paciente virtual.
        data = {
            field: validated_data[field]
            for field in virtual_patient_fields
        }
        # Define a data de atualização como o momento atual.
        data["updated_at"] = datetime.now()
        # Gera um código de vínculo aleatório.
        data["bind_code"] = random.randrange(0, 1048576) 
        # Cria o paciente virtual.
        result = VirtualPatient.create(data)
        
        # Para cada comorbidade na lista validada, cria uma `Observation` no OMOP.
        for c in set(validated_data["comorbidities"]):
            obs = Observation.objects.create(
                person_id = result["patient_id"],
                observation_concept_id =  omop_ids.CID_COMORBIDITY, # ID de conceito para comorbidade.
                observation_type_concept_id = omop_ids.CID_EHR, # ID de conceito para tipo de observação (prontuário eletrônico).
                value_as_concept_id = virtual_models.map_comorbidities.virtual_to_db(c), # Valor da comorbidade como ID de conceito OMOP.
                observation_date = data["updated_at"] # Data da observação.
            )
        
        return result
    
    # Valida o campo de gênero usando o descritor do modelo virtual.
    def validate_gender(self, value):
        result = VirtualPatient.descriptor().fields["gender"].validate(value)
        if result != None:
            raise serializers.ValidationError(result)
        return value

class VirtualWoundSerializer(serializers.Serializer):
    # Campo somente leitura para o ID da ferida.
    wound_id      = serializers.IntegerField(read_only=True) 
    # Campo obrigatório para o ID do paciente.
    patient_id    = serializers.IntegerField(required=True) 
    # Campo obrigatório para o ID do especialista.
    specialist_id = serializers.IntegerField(required=True) 
    # Campo somente leitura para a data de última atualização.
    updated_at    = serializers.DateTimeField(read_only=True)
    # Campo obrigatório para a região da ferida, usando choices mapeados.
    region        = serializers.ChoiceField(required=True, choices=virtual_models.map_wound_location.virtual_values())     
    # Campo obrigatório para o tipo da ferida, usando choices mapeados.
    wound_type    = serializers.ChoiceField(required=True, choices=virtual_models.map_wound_type.virtual_values()) 
    # Campo obrigatório para a data de início da ferida.
    start_date    = TimezoneAwareDateField(required=True) 
    # Campo opcional para a data de término da ferida.
    end_date      = TimezoneAwareDateField(allow_null=True, required=False)
    # Campo obrigatório para o status de atividade da ferida.
    is_active     = serializers.BooleanField(required=True)
    # Campo somente leitura para a URL da imagem associada.
    image_url     = serializers.URLField(read_only=True)
    # Campo opcional para o ID da imagem (se já existir).
    image_id      = serializers.IntegerField(allow_null=True)

    # Método auxiliar para validar a existência de um Concept ID.
    def _validate_concept_id_existence(self, value, field_name):
        if value:
            try:
                # Tenta encontrar o Concept com o ID fornecido.
                Concept.objects.get(concept_id=value)
            except Concept.DoesNotExist:
                # Se não encontrado, levanta uma ValidationError.
                raise serializers.ValidationError(
                    f"O Concept ID '{value}' para '{field_name}' não foi encontrado na base de conceitos OMOP."
                )
        return value

    # Valida se a data de início não é no futuro.
    def validate_start_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data de início da ferida não pode ser no futuro.")
        return value

    # Valida se a data de término não é no futuro.
    def validate_end_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data de término da ferida não pode ser no futuro.")
        return value
    

    
class ImageSerializer(serializers.ModelSerializer):
    # Valida o arquivo de imagem, verificando a extensão.
    def validate_image(self, value):
        if not value.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            raise serializers.ValidationError("O arquivo deve ser uma imagem (PNG, JPG, JPEG, GIF).")
        return value
    
    class Meta:
        # Define o modelo associado a este serializer.
        model = Image
        # Define os campos a serem incluídos na serialização/deserialização.
        fields = ['image', 'image_id', 'tissue_type', 'w_i_fi', 'wound_size_cm2']

class VirtualTrackingRecordsSerializer(serializers.Serializer):
    # Campo somente leitura para o ID do registro de acompanhamento.
    tracking_id              = serializers.IntegerField(read_only=True)
    # Campo somente leitura para o ID do paciente (herdado da ferida).
    patient_id               = serializers.IntegerField(read_only=True)
    # Campo somente leitura para o ID do especialista (herdado da ferida).
    specialist_id            = serializers.IntegerField(read_only=True)
    # Campo obrigatório para o ID da ferida associada.
    wound_id                 = serializers.IntegerField(required=True)
    # Campo somente leitura para a data do acompanhamento.
    track_date               = serializers.DateField(read_only=True)
    # Campo opcional para o comprimento da ferida.
    length                   = serializers.FloatField(min_value=0.0, allow_null=True, required=False)
    # Campo opcional para a largura da ferida.
    width                    = serializers.FloatField(min_value=0.0, allow_null=True, required=False)
    # Campo obrigatório (pode ser nulo) para a quantidade de exsudato, com choices mapeados.
    exudate_amount           = serializers.ChoiceField(allow_null=True, required=True, choices=virtual_models.map_exudate_amount.virtual_values()) 
    # Campo obrigatório (pode ser nulo) para o tipo de exsudato, com choices mapeados.
    exudate_type             = serializers.ChoiceField(allow_null=True, required=True, choices=virtual_models.map_exudate_type.virtual_values())    
    # Campo obrigatório (pode ser nulo) para o tipo de tecido, com choices mapeados.
    tissue_type              = serializers.ChoiceField(allow_null=True, required=True, choices=virtual_models.map_tissue_type.virtual_values())
    # Campo obrigatório (pode ser nulo) para as bordas da ferida, com choices mapeados.
    wound_edges              = serializers.ChoiceField(allow_null=True, required=True, choices=virtual_models.map_wound_edges.virtual_values())
    # Campo obrigatório (pode ser nulo) para a pele ao redor, com choices mapeados.
    skin_around              = serializers.ChoiceField(allow_null=True, required=True, choices=virtual_models.map_skin_around.virtual_values())
    # Campo opcional para indicar se o paciente teve febre.
    had_a_fever              = serializers.BooleanField(required=False)
    # Campo opcional para o nível de dor, com faixa de valores de 0 a 10.
    pain_level               = serializers.IntegerField(min_value=0, max_value=10, allow_null=True, required=False)
    # Campo opcional para o número de trocas de curativo por dia.
    dressing_changes_per_day = serializers.IntegerField(min_value=0, allow_null=True, required=False) 
    # Campo opcional para orientações ao paciente.
    guidelines_to_patient    = serializers.CharField(max_length=1000, allow_null=True, required=False, allow_blank=True)
    # Campo opcional para notas extras.
    extra_notes              = serializers.CharField(max_length=1000, allow_null=True, required=False, allow_blank=True)
    # Campo somente leitura para a URL da imagem.
    image_url                = serializers.URLField(read_only=True)
    # Campo para o ID da imagem.
    image_id                 = serializers.IntegerField()
    
    # Método auxiliar para validar a existência de um Concept ID (semelhante ao VirtualWoundSerializer).
    def _validate_concept_id_existence(self, value, field_name):
        if value:
            try:
                Concept.objects.get(concept_id=value)
            except Concept.DoesNotExist:
                raise serializers.ValidationError(
                    f"O Concept ID '{value}' para '{field_name}' não foi encontrado na base de conceitos OMOP."
                )
        return value

    # Valida se a data do acompanhamento não é no futuro.
    def validate_track_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data do acompanhamento não pode ser no futuro.")
        return value
        
class VirtualComorbiditySerializer(VirtualModelSerializer):
    # Campo somente leitura que obtém o nome da comorbidade dinamicamente.
    comorbidity_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        # Define o supermodelo e o modelo associado a este serializer.
        super_model = VirtualComorbidity
        model = VirtualComorbidity
        # Inclui todos os campos do modelo.
        fields = "__all__"
        # Define campos somente leitura.
        read_only_fields = ["comorbidity_id", "comorbidity_name"]

    # Valida se o Concept ID da comorbidade existe.
    def validate_comorbidity_type(self, value):
        # Garante que o concept existe
        if not Concept.objects.filter(concept_id=value).exists():
            raise serializers.ValidationError(f"O conceito com ID {value} não existe. Certifique-se de que ele foi criado.")
        return value

    # Método para obter o nome da comorbidade a partir do seu Concept ID.
    def get_comorbidity_name(self, obj):
        comorbidity_type = None
        # Verifica se o objeto é um dicionário ou uma instância de modelo.
        if isinstance(obj, dict):
            comorbidity_type = obj.get('comorbidity_type')
        else:
            comorbidity_type = getattr(obj, 'comorbidity_type', None)
        if not comorbidity_type:
            return None
        # Busca o Concept correspondente e retorna seu nome.
        concept = Concept.objects.filter(concept_id=comorbidity_type).first()
        return concept.concept_name if concept else None
from django.db import models
from django.utils import timezone
import uuid
import os
from django.contrib.auth import get_user_model
from .omop.omop_models import Person, Provider, ConditionOccurrence, ProcedureOccurrence

User = get_user_model()

class PatientNonClinicalInfos(models.Model):
    person = models.ForeignKey(Person, models.DO_NOTHING)
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    accept_tcl = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    bind_code  = models.IntegerField(unique=True, null=True)
    user  = models.ForeignKey(User, models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    print(instance)
    return os.path.join('images', filename)


""" IMAGES MODEL """
class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to=get_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class WoundImage(models.Model):
    wound_image_id = models.AutoField(primary_key=True)
    image = models.ForeignKey(Image, null=True, on_delete=models.DO_NOTHING)
    wound = models.ForeignKey(ConditionOccurrence, on_delete=models.DO_NOTHING)

class TrackingRecordImage(models.Model):
    tracking_record_image_id = models.AutoField(primary_key=True)
    image = models.ForeignKey(Image, null=True, on_delete=models.DO_NOTHING)
    tracking_record = models.ForeignKey(ProcedureOccurrence, on_delete=models.DO_NOTHING) 

from django.db import models
# from .virtual_models import VirtualPatient # You might import this for type hinting, but not for ForeignKey

class TextoRecebido(models.Model):
    # Foreign key to associate with a patient's ID
    # We use IntegerField because patient_id from VirtualPatient looks like an integer.
    # If it's a string, use CharField.
    patient_id = models.IntegerField(
        help_text="ID do paciente associado a este texto."
    )
    
    conteudo = models.TextField(max_length=2000)
    data_recebimento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Texto de {self.data_recebimento.strftime('%Y-%m-%d %H:%M')} (Paciente: {self.patient_id})"

    class Meta:
        verbose_name = "Texto Recebido"
        verbose_name_plural = "Textos Recebidos"
        ordering = ['-data_recebimento']

TEMPO_MUDANCA_CHOICES = [
    ('HOJE', 'Hoje'),
    ('ONTEM', 'Ontem'),
    ('2-3_DIAS', 'Há 2-3 dias'),
    ('MAIS_3_DIAS', 'Mais de 3 dias'),
]

class AtencaoImediataRegistro(models.Model):
    """
    Representa um registro de atenção imediata para uma ferida específica de um paciente.
    """
    # Associa ao ID do paciente (do seu VirtualPatient)
    patient_id = models.IntegerField(
        help_text="ID do paciente associado a este registro de atenção imediata."
    )
    # Associa ao ID da ferida (do seu VirtualWound), já que as perguntas são sobre a ferida
    wound_id = models.IntegerField(
        help_text="ID da ferida a que este registro de atenção imediata se refere."
    )

    data_registro = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora em que o registro foi criado."
    )

    # Campos de checkbox para "Notou alguma mudança na ferida?"
    aumento_tamanho = models.BooleanField(
        default=False,
        help_text="Indica se a ferida aumentou de tamanho."
    )
    vermelha_inchada = models.BooleanField(
        default=False,
        help_text="Indica se a ferida está mais vermelha ou inchada."
    )
    saindo_pus_secrecao = models.BooleanField(
        default=False,
        help_text="Indica se a ferida está saindo pus ou secreção."
    )
    doendo_mais = models.BooleanField(
        default=False,
        help_text="Indica se a ferida começou a doer mais."
    )
    pele_quente = models.BooleanField(
        default=False,
        help_text="Indica se a pele ao redor da ferida ficou quente."
    )

    # Campo para "Você está com febre ou se sentindo mal?" (Sim/Não)
    com_febre_mal = models.BooleanField(
        default=False,
        help_text="Indica se o paciente está com febre ou se sentindo mal."
    )

    # Campo de escolha para "Há quanto tempo você notou mudança?"
    tempo_mudanca = models.CharField(
        max_length=20, # Tamanho máximo para as opções ('MAIS_3_DIAS')
        choices=TEMPO_MUDANCA_CHOICES,
        null=True, # Permitir que seja nulo se o usuário não selecionar
        blank=True, # Permitir que seja vazio no formulário
        help_text="Há quanto tempo a mudança na ferida foi notada (se aplicável)."
    )

    class Meta:
        verbose_name = "Registro de Atenção Imediata"
        verbose_name_plural = "Registros de Atenção Imediata"
        ordering = ['-data_registro'] # Os mais recentes primeiro

    def __str__(self):
        return f"Atenção Imediata (Paciente: {self.patient_id}, Ferida: {self.wound_id}) - {self.data_registro.strftime('%Y-%m-%d %H:%M')}"

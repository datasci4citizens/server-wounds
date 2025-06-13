from django.core.management.base import BaseCommand
from app_cicatrizando.omop.omop_models import Concept
from app_cicatrizando.omop.omop_ids import (
    CID_DIABETES, CID_HIPERTENSAO, CID_OBESIDADE, CID_DPOC,
    CID_INSUFICIENCIA_CARDIACA, CID_CANCER, CID_ASMA, CID_DOENCA_RENAL_CRONICA
)
from django.db import transaction

class Command(BaseCommand):
    help = 'Adiciona conceitos de comorbidades ao banco de dados'

    @transaction.atomic
    def handle(self, *args, **options):
        comorbidities = [
            (CID_DIABETES, "Diabetes Mellitus"),
            (CID_HIPERTENSAO, "Hipertensão Arterial"),
            (CID_OBESIDADE, "Obesidade"),
            (CID_DPOC, "Doença Pulmonar Obstrutiva Crônica"),
            (CID_INSUFICIENCIA_CARDIACA, "Insuficiência Cardíaca"),
            (CID_CANCER, "Câncer"),
            (CID_ASMA, "Asma"),
            (CID_DOENCA_RENAL_CRONICA, "Doença Renal Crônica"),
        ]
        
        for concept_id, concept_name in comorbidities:
            _, created = Concept.objects.get_or_create(
                concept_id=concept_id,
                defaults={
                    'concept_name': concept_name,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Criado conceito: {concept_name} (ID: {concept_id})'))
            else:
                self.stdout.write(f'Conceito já existe: {concept_name} (ID: {concept_id})')

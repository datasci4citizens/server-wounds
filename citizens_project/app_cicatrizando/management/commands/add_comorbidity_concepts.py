from django.core.management.base import BaseCommand, CommandError
from app_cicatrizando.omop.omop_models import Concept
from app_cicatrizando.omop.omop_ids import (
    CID_DIABETES, CID_HIPERTENSAO, CID_OBESIDADE, CID_DPOC,
    CID_INSUFICIENCIA_CARDIACA, CID_CANCER, CID_ASMA, CID_DOENCA_RENAL_CRONICA
)
from django.db import transaction

import os
import pandas as pd
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

class Command(BaseCommand):
    help = 'Importa conceitos ICD10 de condição do arquivo CONCEPT.csv para o banco de dados OMOP.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Caminho completo para o arquivo CONCEPT.csv',
            default='app_cicatrizando/data/CONCEPT.csv'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file_path = options['path']

        self.stdout.write(f'Iniciando importação de conceitos ICD10 do arquivo: {csv_file_path}')

        try:
            df = pd.read_csv(csv_file_path)

            # Filtra os dados: domain_id como 'Condition' e vocabulary_id como 'ICD10'
            icd10_conditions = df[
                (df['domain_id'] == 'Condition') &
                (df['vocabulary_id'] == 'ICD10')
            ]

            total_imported = 0
            total_skipped_existing = 0
            total_skipped_invalid = 0

            self.stdout.write(f'Encontrados {len(icd10_conditions)} conceitos ICD10 de condição no CSV.')
            self.stdout.write('Processando...')

            # Itera sobre as linhas filtradas e salva no banco de dados
            for index, row in icd10_conditions.iterrows():
                concept_id = row['concept_id']
                concept_name = row['concept_name']

                # Validar se os campos essenciais não são nulos ou vazios
                if pd.isna(concept_id) or pd.isna(concept_name):
                    self.stdout.write(self.style.WARNING(
                        f'Pulando linha {index} devido a valores ausentes para concept_id ou concept_name.'
                    ))
                    total_skipped_invalid += 1
                    continue

                try:
                    concept_id = int(concept_id) # Garante que concept_id é um inteiro
                except ValueError:
                    self.stdout.write(self.style.WARNING(
                        f'Pulando linha {index} devido a concept_id inválido: {concept_id}'
                    ))
                    total_skipped_invalid += 1
                    continue

                # Prepara os dados para o get_or_create
                defaults = {
                    'concept_name': concept_name,
                    'domain_id': row['domain_id'],
                    'vocabulary_id': row['vocabulary_id'],
                    'concept_class_id': row['concept_class_id'],
                    'standard_concept': row['standard_concept'] if pd.notna(row['standard_concept']) else None,
                    'concept_code': row['concept_code'],
                    'valid_start_date': pd.to_datetime(row['valid_start_date']).date() if pd.notna(row['valid_start_date']) else None,
                    'valid_end_date': pd.to_datetime(row['valid_end_date']).date() if pd.notna(row['valid_end_date']) else None,
                }

                # Limpeza de valores nan para None antes de passar para o ORM
                for key, value in defaults.items():
                    if pd.isna(value):
                        defaults[key] = None

                try:
                    _, created = Concept.objects.get_or_create(
                        concept_id=concept_id,
                        defaults=defaults
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Criado: {concept_name} (ID: {concept_id})'))
                        total_imported += 1
                    else:
                        self.stdout.write(f'Já existe: {concept_name} (ID: {concept_id}) - Nenhuma alteração feita.')
                        total_skipped_existing += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Erro ao processar conceito {concept_id} ({concept_name}): {e}'
                    ))
                    total_skipped_invalid += 1

        except FileNotFoundError:
            raise CommandError(f'Erro: O arquivo {csv_file_path} não foi encontrado.')
        except pd.errors.EmptyDataError:
            raise CommandError(f'Erro: O arquivo {csv_file_path} está vazio.')
        except pd.errors.ParserError as e:
            raise CommandError(f'Erro de parsing no arquivo CSV: {e}. Verifique a formatação do CSV.')
        except Exception as e:
            raise CommandError(f'Ocorreu um erro inesperado durante a importação: {e}')

        self.stdout.write(self.style.SUCCESS('\n--- Resumo da Importação ---'))
        self.stdout.write(self.style.SUCCESS(f'Total de conceitos importados: {total_imported}'))
        self.stdout.write(f'Total de conceitos já existentes (pulados): {total_skipped_existing}')
        self.stdout.write(f'Total de conceitos inválidos/com erro (pulados): {total_skipped_invalid}')
        self.stdout.write(self.style.SUCCESS('Importação concluída!'))

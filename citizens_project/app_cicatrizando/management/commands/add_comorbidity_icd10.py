import pandas as pd
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings # Importa as configurações do Django

# Assumindo que seu modelo Concept está aqui:
from app_cicatrizando.omop.omop_models import Concept

class Command(BaseCommand):
    help = 'Popula o banco de dados com conceitos de comorbidades (domain_id=Condition) do arquivo ICD10_CONCEPT.csv.'

    def handle(self, *args, **options):
        # Define o caminho para o arquivo ICD10_CONCEPT.csv
        # Usa settings.BASE_DIR para garantir que o caminho é absoluto e correto
        filtered_csv_path = os.path.join(settings.BASE_DIR, 'app_cicatrizando', 'data', 'ICD10_CONCEPT.csv')

        # Define o tamanho do chunk para leitura do CSV
        CHUNK_SIZE = 100000

        # Nomes das colunas na ordem correta do seu arquivo ICD10_CONCEPT.csv
        column_names = [
            'concept_id', 'concept_name', 'domain_id', 'vocabulary_id',
            'concept_class_id', 'standard_concept', 'concept_code',
            'valid_start_date', 'valid_end_date', 'invalid_reason'
        ]

        self.stdout.write(f"Iniciando a importação de conceitos de comorbidades do arquivo: {filtered_csv_path}")
        self.stdout.write(f"Processando em chunks de {CHUNK_SIZE} linhas.")

        total_lines_read = 0
        total_conditions_processed = 0
        chunk_num = 0

        try:
            # Carrega o CSV em chunks
            # O separador é uma vírgula (',') porque o script de filtragem padrão salva em CSV padrão.
            # header=None e sem skiprows=1, pois o script de filtragem anterior salva sem cabeçalho.
            chunks = pd.read_csv(
                filtered_csv_path,
                sep=',',
                header=None,
                names=column_names,
                chunksize=CHUNK_SIZE,
                encoding='utf-8'
            )

            for chunk_df in chunks:
                chunk_num += 1
                total_lines_read += len(chunk_df)
                self.stdout.write(f"\n--- Processando chunk {chunk_num} ({len(chunk_df)} linhas, total lido: {total_lines_read}) ---")

                # Verifica se as colunas essenciais existem no chunk atual
                required_cols = ['concept_id', 'concept_name', 'domain_id', 'vocabulary_id']
                if not all(col in chunk_df.columns for col in required_cols):
                    self.stdout.write(self.style.WARNING(f"Aviso: Colunas essenciais ({required_cols}) não encontradas neste chunk. Pulando chunk."))
                    self.stdout.write(self.style.WARNING(f"Colunas encontradas no chunk: {chunk_df.columns.tolist()}"))
                    continue

                # FILTRAGEM: Pega apenas as linhas onde 'domain_id' é 'Condition'
                condition_concepts_chunk = chunk_df[
                    (chunk_df['domain_id'] == 'Condition')
                ]

                if not condition_concepts_chunk.empty:
                    self.stdout.write(f"Encontrados {len(condition_concepts_chunk)} conceitos de condição neste chunk.")
                    # Usamos transaction.atomic para garantir que cada chunk seja processado atomicamente
                    with transaction.atomic():
                        for index, row in condition_concepts_chunk.iterrows():
                            # Certifica-se de que concept_id é um inteiro
                            try:
                                concept_id = int(row['concept_id'])
                            except ValueError:
                                self.stdout.write(self.style.ERROR(f"Erro: concept_id inválido '{row['concept_id']}' na linha {index + 1} do chunk. Pulando esta linha."))
                                continue

                            # Prepara os valores padrão para get_or_create
                            defaults = {
                                'concept_name': str(row['concept_name']),
                                'domain_id': str(row['domain_id']),
                                'vocabulary_id': str(row['vocabulary_id']),
                                'concept_class_id': str(row['concept_class_id']),
                                'standard_concept': str(row['standard_concept']) if pd.notna(row['standard_concept']) else None,
                                'concept_code': str(row['concept_code']),
                                'valid_start_date': row['valid_start_date'],
                                'valid_end_date': row['valid_end_date'],
                                'invalid_reason': str(row['invalid_reason']) if pd.notna(row['invalid_reason']) else None,
                            }

                            obj, created = Concept.objects.get_or_create(
                                concept_id=concept_id,
                                defaults=defaults
                            )

                            if created:
                                self.stdout.write(self.style.SUCCESS(f'Criado conceito: {defaults["concept_name"]} (ID: {concept_id})'))
                            else:
                                self.stdout.write(f'Conceito já existe: {defaults["concept_name"]} (ID: {concept_id}) - Verificando atualizações.')
                                # Lógica para atualizar campos se o objeto já existia e os dados mudaram
                                changed = False
                                for field, value in defaults.items():
                                    # Pega o valor atual do objeto no banco de dados
                                    db_value = getattr(obj, field)

                                    # Converte valores para string para comparação consistente e lida com None
                                    # Isso é importante para campos que podem ser nulos ou ter representações diferentes (e.g., NaN vs None)
                                    str_db_value = str(db_value) if db_value is not None else None
                                    str_new_value = str(value) if value is not None else None

                                    # Compara os valores, ignorando se ambos são considerados "vazios" (None ou string vazia)
                                    if str_db_value != str_new_value:
                                        setattr(obj, field, value)
                                        changed = True
                                if changed:
                                    obj.save()
                                    self.stdout.write(self.style.SUCCESS(f'Conceito atualizado: {defaults["concept_name"]} (ID: {concept_id})'))

                            total_conditions_processed += 1
                else:
                    self.stdout.write("Nenhum conceito de condição encontrado neste chunk.")

            self.stdout.write(self.style.SUCCESS(f"\nProcesso de importação concluído!"))
            self.stdout.write(f"Total de linhas lidas do arquivo filtrado: {total_lines_read}")
            self.stdout.write(self.style.SUCCESS(f"Total de conceitos de condição processados e adicionados/atualizados no banco de dados: {total_conditions_processed}"))

        except FileNotFoundError:
            raise CommandError(f"Erro: O arquivo CSV filtrado não foi encontrado no caminho: {filtered_csv_path}")
        except KeyError as e:
            raise CommandError(f"Erro: Uma das colunas esperadas não foi encontrada após a leitura. Detalhes: {e}. Verifique se os nomes das colunas em `column_names` correspondem exatamente aos do seu arquivo (case-sensitive).")
        except pd.errors.EmptyDataError:
            raise CommandError(f"Erro: O arquivo {filtered_csv_path} está vazio.")
        except pd.errors.ParserError as e:
            raise CommandError(f"Erro de parsing no arquivo CSV: {e}. Verifique a formatação do CSV ou o delimitador. Pode haver um problema persistente na estrutura de alguma linha.")
        except Exception as e:
            raise CommandError(f"Ocorreu um erro inesperado: {e}")
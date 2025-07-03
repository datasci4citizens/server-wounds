import pandas as pd
import os

# Define o caminho do arquivo original
file_path = 'citizens_project/app_cicatrizando/data/CONCEPT.csv'

# Define o caminho para o novo arquivo CSV
output_file_path = 'citizens_project/app_cicatrizando/data/CONDITION_ICD10_CONCEPT.csv'

try:
    # Carrega o arquivo CSV
    # O separador parece ser tab (\t) ou múltiplos espaços, vamos tentar ' ' e ajustar 'sep' se necessário
    # Para múltiplos espaços, engine='python' e sep='\s+' costumam funcionar bem
    df = pd.read_csv(file_path, sep='\s+', engine='python')

    # Filtra as linhas
    filtered_df = df[(df['domain_id'] == 'Condition') & (df['vocabulary_id'] == 'ICD10')]

    # Salva o DataFrame filtrado em um novo arquivo CSV
    filtered_df.to_csv(output_file_path, index=False)

    print(f"Arquivo filtrado salvo com sucesso em: {output_file_path}")

except FileNotFoundError:
    print(f"Erro: O arquivo '{file_path}' não foi encontrado. Verifique o caminho.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")

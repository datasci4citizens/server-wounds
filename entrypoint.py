import os
import subprocess
import sys

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

diretorio_django = os.path.join(diretorio_atual, 'citizens_project')

def executar_comando(comando):
    print(f"==> Executando: {' '.join(comando)}")
    try:
        subprocess.run(comando, cwd=diretorio_django, check=True)
    except subprocess.CalledProcessError as erro:
        print(f"\n[ERRO] O comando falhou. Código de saída: {erro.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    print("Iniciando o Entrypoint Multiplataforma...")
    
    python_bin = sys.executable

    executar_comando([python_bin, "manage.py", "migrate"])
    
    executar_comando([python_bin, "manage.py", "runserver", "0.0.0.0:8000"])

    print("Entrypoint finalizado!")
    
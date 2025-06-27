#!/usr/bin/env python3
"""
Script para verificar e instalar dependências do projeto
"""
import sys
import subprocess
import importlib
import pkg_resources

def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    print(f"🐍 Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️ AVISO: Python 3.8+ recomendado")
    else:
        print("✅ Versão do Python adequada")
    
    return True

def get_installed_packages():
    """Lista pacotes instalados"""
    try:
        installed = {pkg.project_name.lower(): pkg.version for pkg in pkg_resources.working_set}
        return installed
    except Exception as e:
        print(f"Erro listando pacotes: {e}")
        return {}

def check_package(package_name, min_version=None, import_name=None):
    """
    Verifica se um pacote está instalado e funcional
    """
    if import_name is None:
        import_name = package_name
    
    try:
        # Tentar importar
        module = importlib.import_module(import_name)
        
        # Verificar versão se aplicável
        version = getattr(module, '__version__', 'unknown')
        
        print(f"✅ {package_name}: {version}")
        return True, version
        
    except ImportError as e:
        print(f"❌ {package_name}: Não instalado ({e})")
        return False, None
    except Exception as e:
        print(f"⚠️ {package_name}: Erro ({e})")
        return False, None

def check_all_dependencies():
    """Verifica todas as dependências necessárias"""
    print("="*50)
    print("🔍 VERIFICANDO DEPENDÊNCIAS")
    print("="*50)
    
    # Dependências essenciais para o projeto
    dependencies = [
        # Core ML
        ("tensorflow", "2.8.0", "tensorflow"),
        ("keras", None, "keras"),
        ("numpy", "1.21.0", "numpy"),
        ("scipy", "1.7.0", "scipy"),
        ("scikit-learn", "1.0.0", "sklearn"),
        
        # Visão computacional
        ("opencv-python", "4.5.0", "cv2"),
        ("pillow", "8.0.0", "PIL"),
        
        # Visualização
        ("matplotlib", "3.5.0", "matplotlib"),
        
        # Utilidades
        ("protobuf", "3.19.0", "google.protobuf"),
        
        # Para ONNX (opcionais)
        ("tf2onnx", None, "tf2onnx"),
        ("onnxruntime", None, "onnxruntime"),
    ]
    
    missing = []
    working = []
    
    for package, min_version, import_name in dependencies:
        success, version = check_package(package, min_version, import_name)
        if success:
            working.append((package, version))
        else:
            missing.append((package, min_version or "latest"))
    
    print("\n" + "="*50)
    print("📊 RESUMO")
    print("="*50)
    print(f"✅ Funcionando: {len(working)}")
    print(f"❌ Faltando: {len(missing)}")
    
    if missing:
        print(f"\n📦 PACOTES FALTANDO:")
        for package, version in missing:
            print(f"  - {package}>={version}")
    
    return missing, working

def generate_updated_requirements():
    """Gera requirements.txt atualizado"""
    
    # Versões testadas e compatíveis
    requirements = [
        "# Dependências principais do projeto",
        "tensorflow>=2.10.0,<2.15.0  # Core ML framework",
        "keras>=2.10.0  # High-level API",
        "numpy>=1.21.0,<1.25.0  # Numerical computing",
        "scipy>=1.9.0  # Scientific computing",
        "scikit-learn>=1.1.0  # ML utilities",
        "",
        "# Visão computacional",
        "opencv-python>=4.6.0  # Computer vision",
        "pillow>=9.0.0  # Image processing",
        "",
        "# Visualização e plotting",
        "matplotlib>=3.5.0  # Plotting",
        "",
        "# Protobuf (compatibilidade TensorFlow)",
        "protobuf>=3.19.0,<4.0.0  # Protocol buffers",
        "",
        "# ONNX export (opcional)",
        "tf2onnx>=1.13.0  # TensorFlow to ONNX conversion",
        "onnxruntime>=1.12.0  # ONNX inference",
        "",
        "# Desenvolvimento (opcional)",
        "jupyter>=1.0.0  # Notebooks",
        "tqdm>=4.64.0  # Progress bars",
    ]
    
    return "\n".join(requirements)

def install_missing_packages(missing_packages):
    """Instala pacotes faltando"""
    if not missing_packages:
        print("✅ Todas as dependências estão instaladas!")
        return
    
    print(f"\n🔧 INSTALANDO {len(missing_packages)} PACOTES...")
    
    # Criar comando pip
    packages_to_install = []
    for package, version in missing_packages:
        if version and version != "latest":
            packages_to_install.append(f"{package}>={version}")
        else:
            packages_to_install.append(package)
    
    cmd = [sys.executable, "-m", "pip", "install"] + packages_to_install
    
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Instalação concluída!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("🚀 VERIFICADOR DE DEPENDÊNCIAS")
    print("="*50)
    
    # Verificar Python
    check_python_version()
    
    # Verificar dependências
    missing, working = check_all_dependencies()
    
    # Gerar requirements atualizado
    updated_req = generate_updated_requirements()
    
    print(f"\n📝 REQUIREMENTS.TXT ATUALIZADO:")
    print("-" * 30)
    print(updated_req)
    
    # Salvar requirements
    with open("requirements_updated.txt", "w") as f:
        f.write(updated_req)
    
    print(f"\n💾 Salvo em: requirements_updated.txt")
    
    # Oferecer instalação automática
    if missing:
        print(f"\n❓ Deseja instalar os pacotes faltando? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes', 's', 'sim']:
                install_missing_packages(missing)
                
                # Verificar novamente
                print(f"\n🔄 Verificando instalação...")
                missing_after, _ = check_all_dependencies()
                
                if not missing_after:
                    print(f"\n🎉 SUCESSO! Todas as dependências instaladas!")
                    print(f"▶️ Agora você pode executar: python3 train2.py")
                else:
                    print(f"\n⚠️ Alguns pacotes ainda faltam. Tente instalação manual:")
                    print(f"pip install -r requirements_updated.txt")
            else:
                print(f"\n💡 Para instalar manualmente:")
                print(f"pip install -r requirements_updated.txt")
        except KeyboardInterrupt:
            print(f"\n\n👋 Cancelado pelo usuário")
    else:
        print(f"\n🎉 Todas as dependências estão OK!")
        print(f"▶️ Você pode executar: python3 train2.py")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Script para corrigir imports do Keras em todos os arquivos do projeto
"""
import os
import re
import glob

def fix_keras_imports_in_file(filepath):
    """
    Corrige imports do Keras em um arquivo específico
    """
    print(f"🔧 Corrigindo: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Substituições principais
        replacements = [
            # Imports básicos
            (r'from keras\.models import', 'from tensorflow.keras.models import'),
            (r'from keras\.layers import', 'from tensorflow.keras.layers import'),
            (r'from keras\.callbacks import', 'from tensorflow.keras.callbacks import'),
            (r'from keras\.optimizers import', 'from tensorflow.keras.optimizers import'),
            (r'from keras\.losses import', 'from tensorflow.keras.losses import'),
            (r'from keras\.metrics import', 'from tensorflow.keras.metrics import'),
            (r'from keras\.utils import', 'from tensorflow.keras.utils import'),
            (r'from keras\.preprocessing import', 'from tensorflow.keras.preprocessing import'),
            (r'from keras\.applications import', 'from tensorflow.keras.applications import'),
            
            # Imports específicos
            (r'from tensorflow.keras import backend as K', 'from tensorflow.keras import backend as K'),
            (r'import tensorflow.keras as keras\.backend as K', 'import tensorflow.keras.backend as K'),
            (r'from tensorflow.keras.models import Model', 'from tensorflow.keras.models import Model'),
            (r'from tensorflow.keras.layers import Input', 'from tensorflow.keras.layers import Input'),
            
            # Utils que mudaram de local
            (r'from keras\.utils\.generic_utils import', 'from tensorflow.keras.utils import'),
            (r'keras\.utils\.generic_utils\.', 'tensorflow.keras.utils.'),
            
            # Imports diretos
            (r'import tensorflow.keras as keras\b', 'import tensorflow.keras as keras'),
            
            # Casos específicos problemáticos
            (r'from keras\.models import Model, Input', 'from tensorflow.keras.models import Model\nfrom tensorflow.keras.layers import Input'),
        ]
        
        # Aplicar substituições
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Verificar se houve mudanças
        if content != original_content:
            # Fazer backup
            backup_path = filepath + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Salvar arquivo corrigido
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✅ Corrigido! Backup salvo em: {backup_path}")
            return True
        else:
            print(f"  ⚪ Nenhuma mudança necessária")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def find_python_files():
    """
    Encontra todos os arquivos Python no projeto
    """
    patterns = [
        '*.py',
        'models/*.py', 
        'utils/**/*.py',
        'utils/*.py'
    ]
    
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))
    
    # Remover duplicatas e arquivos de backup
    files = list(set(files))
    files = [f for f in files if not f.endswith('.backup')]
    
    return sorted(files)

def main():
    """
    Função principal
    """
    print("🚀 Corrigindo imports do Keras para TensorFlow 2.x")
    print("=" * 55)
    
    # Encontrar arquivos Python
    python_files = find_python_files()
    print(f"📁 Encontrados {len(python_files)} arquivos Python:")
    for f in python_files:
        print(f"  - {f}")
    
    print("\n🔧 Iniciando correções...")
    
    # Corrigir cada arquivo
    fixed_count = 0
    for filepath in python_files:
        if fix_keras_imports_in_file(filepath):
            fixed_count += 1
    
    print(f"\n📊 Resultado:")
    print(f"  ✅ Arquivos corrigidos: {fixed_count}")
    print(f"  📁 Total processados: {len(python_files)}")
    
    if fixed_count > 0:
        print(f"\n💾 Backups criados com extensão .backup")
        print(f"💡 Para restaurar um arquivo: mv arquivo.py.backup arquivo.py")
    
    print(f"\n🎯 Próximos passos:")
    print(f"  1. python train2.py")
    print(f"  2. Se houver erro, verificar logs acima")
    
    # Teste rápido de imports
    print(f"\n🧪 Teste rápido de imports...")
    try:
        from models.unets import Unet2D
        print("✅ models.unets importado com sucesso")
    except Exception as e:
        print(f"❌ Erro em models.unets: {e}")
    
    try:
        from utils.learning.metrics import dice_coef
        print("✅ utils.learning.metrics importado com sucesso")
    except Exception as e:
        print(f"❌ Erro em utils.learning.metrics: {e}")
    
    try:
        from utils.learning.losses import dice_coef_loss
        print("✅ utils.learning.losses importado com sucesso")
    except Exception as e:
        print(f"❌ Erro em utils.learning.losses: {e}")

if __name__ == "__main__":
    main()
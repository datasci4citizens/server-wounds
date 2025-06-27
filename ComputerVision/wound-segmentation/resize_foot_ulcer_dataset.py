#!/usr/bin/env python3
"""
Script para redimensionar dataset Foot_Ulcer_Segmentation_Challenge de 512x512 para 256x256
"""
import os
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time

class FootUlcerResizer:
    def __init__(self, source_dataset='Foot_Ulcer_Segmentation_Challenge', 
                 target_size=(256, 256), output_suffix='_256'):
        """
        Args:
            source_dataset: Nome do dataset source
            target_size: Tamanho alvo (width, height)
            output_suffix: Sufixo para dataset output
        """
        self.source_path = f'./data/{source_dataset}/'
        self.target_size = target_size
        self.output_path = f'./data/{source_dataset}{output_suffix}/'
        
        # Contadores thread-safe
        self.processed_count = 0
        self.error_count = 0
        self.total_files = 0
    
    def verify_source(self):
        """Verifica e analisa o dataset source"""
        print(f"🔍 Analisando dataset: {self.source_path}")
        
        if not os.path.exists(self.source_path):
            print(f"❌ ERRO: {self.source_path} não existe!")
            return False
        
        # Estrutura esperada
        subdirs = ['train/images', 'train/labels', 'validation/images', 'validation/labels', 'test/images']
        
        dataset_info = {}
        total_files = 0
        
        for subdir in subdirs:
            full_path = os.path.join(self.source_path, subdir)
            
            if os.path.exists(full_path):
                files = [f for f in os.listdir(full_path) 
                        if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                dataset_info[subdir] = len(files)
                total_files += len(files)
                print(f"  📁 {subdir}: {len(files)} arquivos")
                
                # Verificar tamanho de uma imagem sample
                if files:
                    sample_path = os.path.join(full_path, files[0])
                    sample_img = cv2.imread(sample_path)
                    if sample_img is not None:
                        h, w = sample_img.shape[:2]
                        print(f"    📐 Tamanho sample: {w}x{h}")
            else:
                print(f"  ⚠️  {subdir}: Não encontrado")
                dataset_info[subdir] = 0
        
        self.total_files = total_files
        print(f"\n📊 Total de arquivos: {total_files}")
        
        if total_files == 0:
            print("❌ Nenhum arquivo encontrado!")
            return False
        
        return True
    
    def create_output_structure(self):
        """Cria estrutura de diretórios para o dataset redimensionado"""
        dirs_to_create = [
            'train/images', 'train/labels',
            'validation/images', 'validation/labels',
            'test/images', 'test/labels'
        ]
        
        print(f"📁 Criando estrutura em: {self.output_path}")
        
        for dir_path in dirs_to_create:
            full_path = os.path.join(self.output_path, dir_path)
            os.makedirs(full_path, exist_ok=True)
        
        print("✅ Estrutura criada")
    
    def resize_single_image(self, input_path, output_path, is_mask=False):
        """Redimensiona uma única imagem"""
        try:
            # Ler imagem
            if is_mask:
                img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
                interpolation = cv2.INTER_NEAREST  # Para máscaras
            else:
                img = cv2.imread(input_path, cv2.IMREAD_COLOR)
                interpolation = cv2.INTER_CUBIC     # Para imagens
            
            if img is None:
                raise ValueError(f"Não foi possível ler: {input_path}")
            
            # Verificar tamanho original
            original_h, original_w = img.shape[:2]
            
            # Redimensionar
            resized = cv2.resize(img, self.target_size, interpolation=interpolation)
            
            # Para máscaras, garantir valores binários
            if is_mask:
                # Binarizar: > 127 vira 255, <= 127 vira 0
                resized = np.where(resized > 127, 255, 0).astype(np.uint8)
            
            # Salvar
            success = cv2.imwrite(output_path, resized)
            
            if not success:
                raise ValueError(f"Falha ao salvar: {output_path}")
            
            # Atualizar contador
            self.processed_count += 1
            
            # Progress a cada 50 arquivos
            if self.processed_count % 50 == 0:
                progress = (self.processed_count / self.total_files) * 100
                print(f"📈 Progresso: {self.processed_count}/{self.total_files} ({progress:.1f}%)")
            
            return True
            
        except Exception as e:
            self.error_count += 1
            print(f"❌ Erro processando {os.path.basename(input_path)}: {e}")
            return False
    
    def process_directory(self, subdir, is_mask=False):
        """Processa um diretório completo"""
        source_dir = os.path.join(self.source_path, subdir)
        target_dir = os.path.join(self.output_path, subdir)
        
        if not os.path.exists(source_dir):
            print(f"⚠️  Pulando {subdir} (não existe)")
            return
        
        # Listar arquivos
        files = [f for f in os.listdir(source_dir) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not files:
            print(f"⚠️  Nenhum arquivo em {subdir}")
            return
        
        file_type = "máscaras" if is_mask else "imagens"
        print(f"🖼️  Processando {subdir}: {len(files)} {file_type}")
        
        # Função para processar arquivo individual
        def process_file(filename):
            input_path = os.path.join(source_dir, filename)
            output_path = os.path.join(target_dir, filename)
            return self.resize_single_image(input_path, output_path, is_mask)
        
        # Processar com threads
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(process_file, files))
        
        end_time = time.time()
        success_count = sum(results)
        
        print(f"✅ {subdir} concluído: {success_count}/{len(files)} OK em {end_time-start_time:.1f}s")
    
    def resize_dataset(self):
        """Redimensiona o dataset completo"""
        print("="*60)
        print(f"🚀 REDIMENSIONANDO: {self.target_size[0]}x{self.target_size[1]}")
        print("="*60)
        
        start_total_time = time.time()
        
        # Verificar source
        if not self.verify_source():
            return False
        
        # Criar estrutura output
        self.create_output_structure()
        
        # Processar diretórios em ordem
        directories = [
            ('train/images', False),
            ('train/labels', True),
            ('validation/images', False),
            ('validation/labels', True),
            ('test/images', False),
            ('test/labels', True)  # Pode não existir
        ]
        
        print("\n🏃‍♂️ Iniciando processamento...")
        
        for subdir, is_mask in directories:
            self.process_directory(subdir, is_mask)
        
        end_total_time = time.time()
        total_time = end_total_time - start_total_time
        
        # Relatório final
        print("\n" + "="*60)
        print("📊 RELATÓRIO FINAL")
        print("="*60)
        print(f"⏱️  Tempo total: {total_time:.1f} segundos ({total_time/60:.1f} min)")
        print(f"✅ Arquivos processados: {self.processed_count}")
        print(f"❌ Erros: {self.error_count}")
        print(f"📁 Dataset salvo em: {self.output_path}")
        
        if self.error_count == 0:
            print("🎉 100% BEM-SUCEDIDO!")
            
            # Calcular redução de tamanho
            original_pixels = 512 * 512
            new_pixels = self.target_size[0] * self.target_size[1]
            reduction = (1 - new_pixels/original_pixels) * 100
            speedup = original_pixels / new_pixels
            
            print(f"📉 Redução de pixels: {reduction:.1f}%")
            print(f"🚀 Speedup esperado no treino: ~{speedup:.1f}x")
        else:
            print(f"⚠️  {self.error_count} arquivos falharam")
        
        return self.error_count == 0
    
    def quick_verify(self):
        """Verificação rápida do output"""
        print("\n🔍 Verificação rápida do resultado...")
        
        test_dirs = ['train/images', 'train/labels']
        
        for test_dir in test_dirs:
            full_path = os.path.join(self.output_path, test_dir)
            if os.path.exists(full_path):
                files = [f for f in os.listdir(full_path) if f.lower().endswith('.png')]
                if files:
                    # Testar primeiro arquivo
                    test_file = os.path.join(full_path, files[0])
                    img = cv2.imread(test_file, cv2.IMREAD_UNCHANGED)
                    if img is not None:
                        h, w = img.shape[:2]
                        if (w, h) == self.target_size:
                            print(f"✅ {test_dir}: {w}x{h} ✓")
                        else:
                            print(f"❌ {test_dir}: {w}x{h} (esperado {self.target_size})")
                    else:
                        print(f"❌ {test_dir}: Erro lendo arquivo teste")

def main():
    """Função principal"""
    print("🖼️  REDIMENSIONADOR FOOT ULCER DATASET")
    print("="*60)
    
    # Configurações
    source = 'Foot_Ulcer_Segmentation_Challenge'
    target_size = (256, 256)  # Pode mudar aqui: (256, 256) para ainda mais rápido
    suffix = '_256'
    
    print(f"📁 Dataset source: {source}")
    print(f"📐 Tamanho alvo: {target_size[0]}x{target_size[1]}")
    print(f"📂 Output: {source}{suffix}")
    
    # Criar resizer
    resizer = FootUlcerResizer(
        source_dataset=source,
        target_size=target_size,
        output_suffix=suffix
    )
    
    # Executar
    success = resizer.resize_dataset()
    
    if success:
        # Verificar resultado
        resizer.quick_verify()
        
        print("\n" + "="*60)
        print("🎉 REDIMENSIONAMENTO CONCLUÍDO!")
        print("="*60)
        print(f"📁 Novo dataset: ./data/{source}{suffix}/")
        print("💡 Para usar no treinamento:")
        print(f"   dataset = '{source}{suffix}'")
        print(f"   input_dim_x = {target_size[0]}")
        print(f"   input_dim_y = {target_size[1]}")
        print("="*60)
    else:
        print("❌ Redimensionamento falhou - verifique os erros acima")

if __name__ == "__main__":
    main()
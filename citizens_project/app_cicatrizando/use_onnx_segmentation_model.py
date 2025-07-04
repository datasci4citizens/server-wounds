"""
Interface simples para usar o modelo ONNX de segmentação de feridas.
Requer apenas: onnxruntime, opencv-python, numpy

Instalação:
pip install onnxruntime opencv-python numpy
"""

import onnxruntime as ort
import cv2
import numpy as np
import os
from typing import Union, Tuple


class WoundSegmentationONNX:
    """Classe para segmentação de feridas usando modelo ONNX"""
    
    def __init__(self, model_path: str = "model_wound_segmentation.onnx"):
        """
        Inicializa o modelo ONNX.
        
        Args:
            model_path: Caminho para o arquivo .onnx
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
        
        # Criar sessão ONNX (detecta GPU automaticamente se disponível)
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        self.session = ort.InferenceSession(model_path, providers=providers)
        
        # Obter nomes de entrada/saída
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        
        print(f"✅ Modelo ONNX carregado: {model_path}")
        print(f"🔧 Executando em: {self.session.get_providers()[0]}")
    
    def preprocess_image(self, image: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int]]:
        """
        Prepara a imagem para o modelo.
        
        Args:
            image: Imagem em formato numpy (BGR do OpenCV)
            
        Returns:
            Tupla (imagem_processada, tamanho_original)
        """
        # Guardar tamanho original
        original_height, original_width = image.shape[:2]
        
        # 1. Redimensionar para 256x256
        image_resized = cv2.resize(image, (256, 256), interpolation=cv2.INTER_LINEAR)
        
        # 2. Converter BGR para RGB
        image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
        
        # 3. Normalizar para [0, 1]
        image_normalized = image_rgb.astype(np.float32) / 255.0
        
        # 4. Transpor de HWC (Height, Width, Channels) para CHW (Channels, Height, Width)
        image_transposed = np.transpose(image_normalized, (2, 0, 1))
        
        # 5. Adicionar dimensão batch (1, C, H, W)
        image_batch = np.expand_dims(image_transposed, axis=0)
        
        return image_batch, (original_height, original_width)
    
    def count_wound_pixels(self, image_path: str) -> int:
        """
        Conta pixels de ferida em uma imagem.
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Número de pixels de ferida no tamanho original da imagem
        """
        # Ler imagem
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Erro ao ler imagem: {image_path}")
        
        # Preprocessar
        processed_image, (orig_h, orig_w) = self.preprocess_image(image)
        
        # Fazer predição
        outputs = self.session.run([self.output_name], {self.input_name: processed_image})
        mask_probabilities = outputs[0][0, 0]  # Remove batch e channel dimensions
        
        # Binarizar máscara (threshold 0.5)
        binary_mask = (mask_probabilities > 0.5).astype(np.uint8)
        
        # Contar pixels em 256x256
        pixels_256 = int(binary_mask.sum())
        
        # Calcular pixels no tamanho original
        total_pixels_original = orig_h * orig_w
        total_pixels_256 = 256 * 256
        scale_factor = total_pixels_original / total_pixels_256
        
        pixels_original = int(pixels_256 * scale_factor)
        
        return pixels_original
    
    def segment_image(self, image_path: str, output_mask_path: str = None) -> dict:
        """
        Segmenta uma imagem e opcionalmente salva a máscara.
        
        Args:
            image_path: Caminho para a imagem
            output_mask_path: Caminho para salvar a máscara (opcional)
            
        Returns:
            Dicionário com informações da segmentação
        """
        # Ler imagem
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Erro ao ler imagem: {image_path}")
        
        # Preprocessar
        processed_image, (orig_h, orig_w) = self.preprocess_image(image)
        
        # Fazer predição
        outputs = self.session.run([self.output_name], {self.input_name: processed_image})
        mask_probabilities = outputs[0][0, 0]
        
        # Binarizar máscara
        binary_mask_256 = (mask_probabilities > 0.5).astype(np.uint8)
        
        # Contar pixels em 256x256
        pixels_256 = int(binary_mask_256.sum())
        
        # Redimensionar máscara para tamanho original
        mask_original = cv2.resize(binary_mask_256, (orig_w, orig_h), 
                                   interpolation=cv2.INTER_NEAREST)
        
        # Calcular pixels no tamanho original
        pixels_original = int(mask_original.sum())
        
        # Calcular porcentagem
        total_pixels = orig_h * orig_w
        percentage = (pixels_original / total_pixels) * 100
        
        # Salvar máscara se solicitado
        if output_mask_path:
            mask_to_save = (mask_original * 255).astype(np.uint8)
            cv2.imwrite(output_mask_path, mask_to_save)
            print(f"💾 Máscara salva: {output_mask_path}")
        
        return {
            'pixel_count': pixels_original,
            'pixel_count_256': pixels_256,
            'percentage': percentage,
            'image_size': (orig_w, orig_h),
            'mask': mask_original
        }


# Função simples para uso direto
def count_wound_pixels_simple(image_path: str, model_path: str = "model_wound_segmentation.onnx") -> int:
    """
    Função simples que conta pixels de ferida em uma imagem.
    
    Args:
        image_path: Caminho da imagem
        model_path: Caminho do modelo ONNX
        
    Returns:
        Número de pixels de ferida
    """
    model = WoundSegmentationONNX(model_path)
    return model.count_wound_pixels(image_path)


# ========== EXEMPLO DE USO ==========
if __name__ == "__main__":
    # Método 1: Usar a classe
    print("=== Método 1: Usando a classe ===")
    segmentator = WoundSegmentationONNX("model_wound_segmentation.onnx")
    
    # Contar pixels apenas
    pixel_count = segmentator.count_wound_pixels("exemplo_ferida.jpg")
    print(f"Pixels de ferida: {pixel_count:,}")
    
    # Segmentação completa com mais informações
    result = segmentator.segment_image("exemplo_ferida.jpg", "mascara_saida.png")
    print(f"Pixels: {result['pixel_count']:,}")
    print(f"Porcentagem: {result['percentage']:.2f}%")
    print(f"Tamanho da imagem: {result['image_size']}")
    
    # Método 2: Usar função simples
    print("\n=== Método 2: Função simples ===")
    pixels = count_wound_pixels_simple("exemplo_ferida.jpg")
    print(f"Pixels de ferida: {pixels:,}")
    
    # Processar múltiplas imagens
    print("\n=== Processamento em lote ===")
    images = ["img1.jpg", "img2.jpg", "img3.jpg"]
    for img in images:
        try:
            pixels = segmentator.count_wound_pixels(img)
            print(f"{img}: {pixels:,} pixels")
        except Exception as e:
            print(f"{img}: Erro - {e}")
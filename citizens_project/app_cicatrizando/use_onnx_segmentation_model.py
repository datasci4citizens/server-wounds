import onnxruntime as ort
import cv2
import numpy as np
import os
from typing import Union, Tuple
from PIL import Image


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
    
    def preprocess_image(self, image_input: Union[str, Image.Image]) -> Tuple[np.ndarray, Tuple[int, int]]:
        """
        Prepara a imagem para o modelo.
        
        Args:
            image_input: Pode ser um caminho de arquivo (str) ou um objeto PIL.Image.Image
            
        Returns:
            Tupla (imagem_processada, tamanho_original)
        """
        # Se for um caminho de arquivo
        if isinstance(image_input, str):
            # Ler imagem com OpenCV
            image = cv2.imread(image_input)
            if image is None:
                raise ValueError(f"Erro ao ler imagem: {image_input}")
            original_height, original_width = image.shape[:2]
        # Se for um objeto PIL Image
        elif isinstance(image_input, Image.Image):
            # Converter PIL Image para array numpy no formato BGR (que o OpenCV espera)
            image = np.array(image_input)
            # Convert RGB to BGR
            image = image[:, :, ::-1].copy()
            original_height, original_width = image.shape[:2]
        else:
            raise ValueError("Tipo de entrada inválido. Deve ser um caminho de arquivo ou objeto PIL.Image.Image")
        
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
    
    def count_wound_pixels(self, image_input: Union[str, Image.Image]) -> int:
        """
        Conta pixels de ferida em uma imagem.
        
        Args:
            image_input: Pode ser um caminho de arquivo (str) ou um objeto PIL.Image.Image
            
        Returns:
            Número de pixels de ferida no tamanho original da imagem
        """
        # Preprocessar
        processed_image, (orig_h, orig_w) = self.preprocess_image(image_input)
        
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
    
    def segment_image(self, image_input: Union[str, Image.Image], output_mask_path: str = None) -> dict:
        """
        Segmenta uma imagem e opcionalmente salva a máscara.
        
        Args:
            image_input: Pode ser um caminho de arquivo (str) ou um objeto PIL.Image.Image
            output_mask_path: Caminho para salvar a máscara (opcional)
            
        Returns:
            Dicionário com informações da segmentação
        """
        # Preprocessar
        processed_image, (orig_h, orig_w) = self.preprocess_image(image_input)
        
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
def count_wound_pixels_simple(image_input: Union[str, Image.Image], model_path: str = "model_wound_segmentation.onnx") -> int:
    """
    Função simples que conta pixels de ferida em uma imagem.
    
    Args:
        image_input: Pode ser um caminho de arquivo (str) ou um objeto PIL.Image.Image
        model_path: Caminho do modelo ONNX
        
    Returns:
        Número de pixels de ferida
    """
    model = WoundSegmentationONNX(model_path)
    return model.count_wound_pixels(image_input)
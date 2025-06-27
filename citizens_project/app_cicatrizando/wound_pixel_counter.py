import cv2
import os
import numpy as np
from keras.models import load_model
from keras.utils.generic_utils import CustomObjectScope
from tensorflow.keras.losses import binary_crossentropy

from models.unets import Unet2D
from utils.learning.metrics import dice_coef, precision, recall
from utils.learning.losses import dice_coef_loss


class WoundPixelCounter:
    """
    Classe simples para contar pixels de ferida em imagens.
    Focada apenas em retornar valores inteiros para uso em outros módulos.
    """
    
    def __init__(self, model_path, input_dim_x=224, input_dim_y=224, n_filters=16):
        """
        Args:
            model_path: Caminho para o arquivo .hdf5 do modelo
            input_dim_x: Largura esperada pelo modelo
            input_dim_y: Altura esperada pelo modelo
            n_filters: Número de filtros base do modelo
        """
        self.model_path = model_path
        self.input_dim_x = input_dim_x
        self.input_dim_y = input_dim_y
        self.n_filters = n_filters
        self.model = None
        
        # Carregar modelo
        self._load_model()
    
    def _combined_loss(self, y_true, y_pred):
        """Loss function para carregar o modelo"""
        bce_weight = 0.5
        dice_weight = 0.5
        bce = binary_crossentropy(y_true, y_pred)
        dice = dice_coef_loss(y_true, y_pred)
        return bce_weight * bce + dice_weight * dice
    
    def _load_model(self):
        """Carrega o modelo treinado silenciosamente"""
        try:
            self.model = load_model(
                self.model_path,
                custom_objects={
                    'recall': recall,
                    'precision': precision,
                    'dice_coef': dice_coef,
                    'dice_coef_loss': dice_coef_loss,
                    'combined_loss': self._combined_loss
                }
            )
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar modelo: {e}")
    
    def _preprocess_image(self, image_path):
        """
        Pré-processa imagem para o formato esperado pelo modelo
        Returns: np.array pronto para predição
        """
        # Ler imagem
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Não foi possível ler a imagem: {image_path}")
        
        # Redimensionar
        resized = cv2.resize(image, (self.input_dim_y, self.input_dim_x))
        
        # Normalizar (0-1)
        normalized = resized.astype(np.float32) / 255.0
        
        # Adicionar dimensão do batch
        batch_image = np.expand_dims(normalized, axis=0)
        
        return batch_image
    
    def count_wound_pixels(self, image_path, threshold=0.5):
        """
        Conta pixels de ferida em uma imagem.
        
        Args:
            image_path: Caminho para a imagem
            threshold: Threshold para binarização (0.0-1.0)
            
        Returns:
            int: Número de pixels classificados como ferida
        """
        # Pré-processar
        batch_image = self._preprocess_image(image_path)
        
        # Predição
        prediction = self.model.predict(batch_image, verbose=0)
        
        # Processar máscara
        mask_pred = prediction[0]
        
        # Se tem múltiplos canais, usar o primeiro
        if len(mask_pred.shape) == 3 and mask_pred.shape[-1] > 1:
            mask_pred = mask_pred[:, :, 0]
        
        # Garantir 2D
        if len(mask_pred.shape) == 3:
            mask_pred = np.squeeze(mask_pred)
        
        # Binarizar e contar
        binary_mask = (mask_pred > threshold).astype(np.uint8)
        wound_pixels = int(np.sum(binary_mask))
        
        return wound_pixels
    
    def count_wound_pixels_batch(self, image_paths, threshold=0.5):
        """
        Conta pixels de ferida para múltiplas imagens.
        
        Args:
            image_paths: Lista de caminhos para imagens
            threshold: Threshold para binarização
            
        Returns:
            list: Lista de inteiros com pixels de ferida para cada imagem
        """
        results = []
        for image_path in image_paths:
            try:
                pixels = self.count_wound_pixels(image_path, threshold)
                results.append(pixels)
            except Exception:
                results.append(0)  # Retorna 0 em caso de erro
        
        return results
    
    def get_wound_percentage(self, image_path, threshold=0.5):
        """
        Calcula porcentagem de área de ferida.
        
        Args:
            image_path: Caminho para a imagem
            threshold: Threshold para binarização
            
        Returns:
            float: Porcentagem de pixels de ferida (0.0-100.0)
        """
        wound_pixels = self.count_wound_pixels(image_path, threshold)
        total_pixels = self.input_dim_x * self.input_dim_y
        percentage = (wound_pixels / total_pixels) * 100.0
        
        return percentage


# Função standalone para uso direto
def count_pixels_simple(model_path, image_path, threshold=0.5, 
                       input_dim_x=224, input_dim_y=224, n_filters=16):
    """
    Função simples para contar pixels sem instanciar classe.
    
    Args:
        model_path: Caminho para modelo .hdf5
        image_path: Caminho para imagem
        threshold: Threshold para binarização
        input_dim_x, input_dim_y, n_filters: Configurações do modelo
        
    Returns:
        int: Número de pixels de ferida
    """
    counter = WoundPixelCounter(model_path, input_dim_x, input_dim_y, n_filters)
    return counter.count_wound_pixels(image_path, threshold)


# Exemplo de uso direto
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python wound_pixel_counter.py <modelo.hdf5> <imagem.png> [threshold]")
        print("Exemplo: python wound_pixel_counter.py modelo.hdf5 ferida.png 0.5")
        sys.exit(1)
    
    model_path = sys.argv[1]
    image_path = sys.argv[2]
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    
    try:
        # Uso direto da função
        pixels = count_pixels_simple(model_path, image_path, threshold)
        print(pixels)  # Apenas o número
        
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
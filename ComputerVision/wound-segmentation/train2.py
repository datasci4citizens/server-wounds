import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import binary_crossentropy
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, LearningRateScheduler
from tensorflow.keras.models import load_model, Model
# Fix para imports do Keras
try:
    from tensorflow.keras.utils import CustomObjectScope
except ImportError:
    from tensorflow.keras.utils import CustomObjectScope

from tensorflow.keras.layers import Input, Lambda
import tensorflow.keras.backend as K
import os
import numpy as np
import datetime

from models.unets import Unet2D
#from models.deeplab import Deeplabv3, relu6, DepthwiseConv2D, BilinearUpsampling
#from models.FCN import FCN_Vgg16_16s
#from models.SegNet import SegNet

from utils.learning.metrics import dice_coef, precision, recall
from utils.learning.losses import dice_coef_loss
from utils.io.data import DataGen, save_results, save_history, load_data

# COMBINED LOSS FUNCTION
def combined_loss(y_true, y_pred):
    """
    Combina Binary Crossentropy + Dice Loss
    - Binary CE: precisão pixel-a-pixel
    - Dice Loss: sobreposição de regiões
    """
    bce_weight = 0.30  # 30% Binary Crossentropy (reduzido)
    dice_weight = 0.70  # 70% Dice Loss (aumentado - melhor para segmentação)
    
    bce = binary_crossentropy(y_true, y_pred)
    dice = dice_coef_loss(y_true, y_pred)
    
    return bce_weight * bce + dice_weight * dice

# LEARNING RATE SCHEDULER OTIMIZADO
def lr_schedule(epoch):
    """LR Schedule otimizado para 100 épocas"""
    if epoch < 10:
        return 2e-3      # LR alto para início rápido
    elif epoch < 30:
        return 1e-3      # LR médio
    elif epoch < 60:
        return 5e-4      # LR baixo
    elif epoch < 80:
        return 2e-4      # LR muito baixo
    else:
        return 1e-4      # LR mínimo

# PARÂMETROS OTIMIZADOS
input_dim_x = 512
input_dim_y = 512
n_filters = 8  # ← AUMENTADO de 4 para 16 (melhor capacidade)
dataset = 'Foot_Ulcer_Segmentation_Challenge'
data_gen = DataGen('./data/' + dataset + '/', split_ratio=0.2, x=input_dim_x, y=input_dim_y)

# MODELO U-NET
unet2d = Unet2D(n_filters=n_filters, input_dim_x=input_dim_x, input_dim_y=input_dim_y, num_channels=3)
model, model_name = unet2d.get_unet_model_yuanqing()

# HIPERPARÂMETROS OTIMIZADOS
batch_size = 2          # ← AUMENTADO de 4 para 8
epochs = 10            # Conforme solicitado
initial_learning_rate = 1e-4  # ← AUMENTADO de 1e-4 para 2e-3
loss_function = combined_loss

# CALLBACKS OTIMIZADOS
early_stopping = EarlyStopping(
    monitor='val_dice_coef',
    patience=15,         # ← AUMENTADO de 5 para 15 (mais paciência)
    mode='max',
    restore_best_weights=True,
    verbose=1,
    min_delta=0.0005     # ← REDUZIDO threshold
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_dice_coef',
    factor=0.7,          # ← Redução mais suave (era 0.5)
    patience=8,          # ← AUMENTADO de 5 para 8
    min_lr=1e-6,         # ← AUMENTADO de 1e-7 para 1e-6
    verbose=1,
    mode='max'
)

lr_scheduler = LearningRateScheduler(lr_schedule, verbose=1)

# COMPILAR MODELO
model.compile(
    optimizer=Adam(learning_rate=initial_learning_rate, beta_1=0.9, beta_2=0.999),
    loss=loss_function,
    metrics=[dice_coef, precision, recall]
)

# INFO DO DATASET
print("="*60)
print("CONFIGURAÇÃO OTIMIZADA PARA ONNX EXPORT")
print("="*60)
print(f"Modelo: {model_name}")
print(f"Filtros: {n_filters}")
print(f"Batch size: {batch_size}")
print(f"Epochs: {epochs}")
print(f"Learning rate inicial: {initial_learning_rate}")
print(f"Loss function: Combined (30% BCE + 70% Dice)")
print(f"Imagens de treino: {data_gen.get_num_data_points(train=True)}")
print(f"Imagens de validação: {data_gen.get_num_data_points(val=True)}")
print("="*60)

# Verificar dados
train_samples = data_gen.get_num_data_points(train=True)
val_samples = data_gen.get_num_data_points(val=True)

if train_samples == 0:
    print("❌ ERRO: Nenhum dado encontrado!")
    print(f"Verifique se existe: ./data/{dataset}/")
    exit(1)

# TREINAR
print("🚀 Iniciando treinamento...")
training_history = model.fit(
    data_gen.generate_data(batch_size=batch_size, train=True),
    steps_per_epoch=int(train_samples / batch_size),
    callbacks=[early_stopping, reduce_lr, lr_scheduler],
    validation_data=data_gen.generate_data(batch_size=batch_size, val=True),
    validation_steps=int(val_samples / batch_size) if val_samples > 0 else 1,
    epochs=epochs,
    verbose=1
)

# SALVAR .HDF5 TRADICIONAL
print("💾 Salvando modelo tradicional...")
save_history(model, model_name + '_onnx_ready', training_history, dataset, 
             n_filters, epochs, initial_learning_rate, 'combined_loss', 
             color_space='RGB', path='./training_history/')

# ========== CRIAR MODELO COMPLETO PARA ONNX ==========
print("="*60)
print("🔄 CRIANDO MODELO COMPLETO PARA ONNX")
print("="*60)

def create_complete_model(base_model, input_shape=(224, 224, 3)):
    """
    Cria modelo que inclui pré-processamento e pós-processamento
    """
    # Input que aceita qualquer tamanho de imagem
    input_layer = Input(shape=(None, None, 3), name='image_input')
    
    # Pré-processamento integrado
    def preprocess(x):
        # Converter para float32
        x = tf.cast(x, tf.float32)
        
        # Redimensionar para tamanho fixo
        x = tf.image.resize(x, [input_shape[0], input_shape[1]])
        
        # Normalizar (0-1)
        x = x / 255.0
        
        return x
    
    # Pós-processamento integrado
    def postprocess(x):
        # Se múltiplos canais, usar primeiro
        if len(x.shape) == 4 and x.shape[-1] > 1:
            x = x[:, :, :, 0]
        
        # Expandir dimensões se necessário
        if len(x.shape) == 3:
            x = tf.expand_dims(x, -1)
        
        # Binarizar com threshold 0.5
        binary_mask = tf.cast(x > 0.5, tf.float32)
        
        # Contar pixels (reduzir dimensões batch e spatial)
        pixel_count = tf.reduce_sum(binary_mask, axis=[1, 2, 3])
        
        return {
            'binary_mask': binary_mask,
            'raw_prediction': x,
            'pixel_count': pixel_count
        }
    
    # Pipeline completo
    preprocessed = Lambda(preprocess, name='preprocess')(input_layer)
    prediction = base_model(preprocessed)
    outputs = Lambda(postprocess, name='postprocess')(prediction)
    
    complete_model = Model(inputs=input_layer, outputs=outputs, name='WoundSegmentationComplete')
    
    return complete_model

# Criar modelo completo
print("🔧 Integrando pré e pós-processamento...")
complete_model = create_complete_model(model)

print("📐 Estrutura do modelo completo:")
complete_model.summary()

# ========== EXPORTAR PARA ONNX ==========
print("="*60)
print("📦 EXPORTANDO PARA ONNX")
print("="*60)

# Timestamp para nomes únicos
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
export_dir = f"./exported_models/{timestamp}"
os.makedirs(export_dir, exist_ok=True)

# 1. Salvar como SavedModel primeiro
savedmodel_path = f"{export_dir}/complete_model"
print(f"1️⃣ Salvando SavedModel completo: {savedmodel_path}")

# Definir signature específica para ONNX
@tf.function
def serving_fn(image_input):
    return complete_model(image_input)

# Criar signature concreta
concrete_fn = serving_fn.get_concrete_function(
    tf.TensorSpec(shape=[1, None, None, 3], dtype=tf.uint8, name='image_input')
)

# Salvar com signature
tf.saved_model.save(
    complete_model, 
    savedmodel_path, 
    signatures={'serving_default': concrete_fn}
)

print("✅ SavedModel completo salvo!")

# 2. Converter para ONNX
onnx_path = f"{export_dir}/wound_segmentation_complete.onnx"
print(f"2️⃣ Tentando converter para ONNX: {onnx_path}")

try:
    # Verificar se tf2onnx está instalado
    import tf2onnx
    
    # Comando de conversão
    conversion_cmd = f"""python -m tf2onnx.convert --saved-model {savedmodel_path} --output {onnx_path} --opset 11 --verbose"""
    
    print("🔄 Executando conversão...")
    result = os.system(conversion_cmd)
    
    if result == 0 and os.path.exists(onnx_path):
        print("✅ ONNX criado com sucesso!")
        
        # Verificar tamanho do arquivo
        onnx_size = os.path.getsize(onnx_path) / (1024*1024)  # MB
        print(f"📊 Tamanho do ONNX: {onnx_size:.1f} MB")
        
    else:
        print("❌ Falha na conversão ONNX")
        print("💡 Instale tf2onnx: pip install tf2onnx")
        
except ImportError:
    print("⚠️ tf2onnx não instalado!")
    print("📥 Instale com: pip install tf2onnx")
    print(f"🔄 Depois execute:")
    print(f"   python -m tf2onnx.convert --saved-model {savedmodel_path} --output {onnx_path}")

# 3. Criar script de uso para ONNX
usage_script = f'''# USO DO MODELO ONNX - INDEPENDENTE E UNIVERSAL!
import onnxruntime as ort
import cv2
import numpy as np

class ONNXWoundSegmentation:
    def __init__(self, model_path="{onnx_path}"):
        """
        Carrega modelo ONNX - funciona com qualquer framework!
        """
        self.session = ort.InferenceSession(model_path)
        
        # Info do modelo
        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [output.name for output in self.session.get_outputs()]
        
        print(f"✅ Modelo ONNX carregado")
        print(f"📥 Input: {{self.input_name}}")
        print(f"📤 Outputs: {{self.output_names}}")
    
    def count_pixels_simple(self, image_path):
        """Versão simplificada - retorna apenas contagem"""
        # Ler imagem
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Não foi possível ler: {{image_path}}")
        
        # Converter BGR -> RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Adicionar dimensão batch
        batch_image = np.expand_dims(image, axis=0).astype(np.uint8)
        
        # Executar inferência
        outputs = self.session.run(
            self.output_names, 
            {{self.input_name: batch_image}}
        )
        
        # Retornar contagem de pixels
        if len(outputs) >= 3:
            return int(outputs[2][0])  # pixel_count
        else:
            # Se estrutura diferente, calcular manualmente
            mask = outputs[0][0]
            binary_mask = (mask > 0.5).astype(np.uint8)
            return int(np.sum(binary_mask))

# EXEMPLO DE USO:
if __name__ == "__main__":
    # Instalar: pip install onnxruntime opencv-python
    
    segmentator = ONNXWoundSegmentation()
    
    # Usar
    pixels = segmentator.count_pixels_simple("minha_ferida.png")
    print(f"Pixels de ferida: {{pixels}}")
'''

usage_path = f"{export_dir}/uso_onnx.py"
with open(usage_path, 'w') as f:
    f.write(usage_script)

# 4. Criar requirements.txt
requirements = """# Dependências mínimas para usar o modelo ONNX
onnxruntime>=1.12.0
opencv-python>=4.6.0
numpy>=1.21.0

# Para GPU (opcional):
# onnxruntime-gpu>=1.12.0
"""

with open(f"{export_dir}/requirements.txt", 'w') as f:
    f.write(requirements)

# RELATÓRIO FINAL
best_dice = max(training_history.history['val_dice_coef']) if 'val_dice_coef' in training_history.history else 0
final_dice = training_history.history['val_dice_coef'][-1] if 'val_dice_coef' in training_history.history else 0
epochs_trained = len(training_history.history['loss'])

print("="*60)
print("🎉 TREINAMENTO E EXPORTAÇÃO CONCLUÍDOS!")
print("="*60)
print(f"📊 Épocas treinadas: {epochs_trained}")
print(f"🎯 Melhor Dice Score: {best_dice:.4f}")
print(f"📈 Dice Score final: {final_dice:.4f}")
print(f"📁 Arquivos exportados em: {export_dir}")
print("")
print("📋 Arquivos criados:")
print(f"  ✅ SavedModel: {savedmodel_path}")
if os.path.exists(onnx_path):
    print(f"  ✅ ONNX: {onnx_path}")
print(f"  📝 Script de uso: {usage_path}")
print(f"  📦 Requirements: {export_dir}/requirements.txt")
print("")
print("💡 Para usar o modelo ONNX:")
print(f"  1. cd {export_dir}")
print("  2. pip install -r requirements.txt")
print("  3. python uso_onnx.py")
print("")
print("🌍 O modelo ONNX funciona com:")
print("  - PyTorch")
print("  - TensorFlow")
print("  - Scikit-learn")
print("  - C++/C#/Java")
print("  - Qualquer framework!")
print("="*60)
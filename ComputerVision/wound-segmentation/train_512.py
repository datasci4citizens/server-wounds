from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import binary_crossentropy
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, LearningRateScheduler
from keras.models import load_model
from keras.utils.generic_utils import CustomObjectScope
import keras.backend as K
import tensorflow as tf

from models.unets import Unet2D
from models.deeplab import Deeplabv3, relu6, DepthwiseConv2D, BilinearUpsampling
from models.FCN import FCN_Vgg16_16s
from models.SegNet import SegNet

from utils.learning.metrics import dice_coef, precision, recall
from utils.learning.losses import dice_coef_loss
from utils.io.data import DataGen, save_results, save_history, load_data

# CONFIGURAÇÃO GPU
print("Verificando GPUs disponíveis:")
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Habilitar crescimento de memória
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"{len(gpus)} GPU(s) configurada(s) com sucesso")
    except RuntimeError as e:
        print(f"Erro na configuração da GPU: {e}")
else:
    print("Nenhuma GPU detectada - usando CPU")

# COMBINED LOSS FUNCTION otimizada para 512x512
def combined_loss(y_true, y_pred):
    """
    Loss function otimizada para imagens de alta resolução
    """
    # Para 512x512, dar mais peso ao Dice Loss
    bce_weight = 0.1   # 10% Binary Crossentropy  
    dice_weight = 0.9  # 90% Dice Loss (priorizar sobreposição de regiões)
    
    # Calcular cada loss
    bce = binary_crossentropy(y_true, y_pred)
    dice = dice_coef_loss(y_true, y_pred)
    
    # Combinar
    return bce_weight * bce + dice_weight * dice

# LEARNING RATE SCHEDULER para alta resolução
def lr_schedule(epoch):
    """
    LR Schedule otimizado para 512x512:
    - Início mais conservador (resolução alta = mais gradientes)
    - Decay mais gradual
    """
    if epoch < 5:
        return 2e-3      # LR inicial moderado
    elif epoch < 15:
        return 1e-3      # LR médio
    elif epoch < 40:
        return 5e-4      # LR baixo
    elif epoch < 80:
        return 2e-4      # LR muito baixo
    else:
        return 1e-4      # LR mínimo

# PARÂMETROS PARA 512x512 COM GPU POTENTE
input_dim_x = 512
input_dim_y = 512
n_filters = 64        # ← AUMENTADO para 64 (aproveitando GPU potente)
dataset = 'Foot_Ulcer_Segmentation_Challenge'
data_gen = DataGen('./data/' + dataset + '/', split_ratio=0.2, x=input_dim_x, y=input_dim_y)

# MODELO U-NET com mais capacidade
unet2d = Unet2D(n_filters=n_filters, input_dim_x=input_dim_x, input_dim_y=input_dim_y, num_channels=3)
model, model_name = unet2d.get_unet_model_yuanqing()

# HIPERPARÂMETROS PARA GPU POTENTE
batch_size = 6        # ← Otimizado para 512x512 (evita OOM)
epochs = 150          # ← Reduzido (alta resolução converge mais rápido)
initial_learning_rate = 2e-3  # ← Mais conservador para 512x512
loss_function = combined_loss

# CALLBACKS OTIMIZADOS PARA ALTA RESOLUÇÃO
# 1. EarlyStopping
early_stopping = EarlyStopping(
    monitor='val_dice_coef',
    patience=20,           # ← Paciência moderada
    mode='max',
    restore_best_weights=True,
    verbose=1,
    min_delta=0.0005       # ← Threshold menor para alta resolução
)

# 2. ReduceLROnPlateau
reduce_lr = ReduceLROnPlateau(
    monitor='val_dice_coef',
    factor=0.7,            # ← Redução mais suave (0.7 ao invés de 0.5)
    patience=8,            # ← Paciência menor
    min_lr=5e-6,
    verbose=1,
    mode='max'
)

# 3. LearningRateScheduler
lr_scheduler = LearningRateScheduler(lr_schedule, verbose=1)

# COMPILAR MODELO
model.compile(
    optimizer=Adam(learning_rate=initial_learning_rate, beta_1=0.9, beta_2=0.999),
    loss=loss_function,
    metrics=[dice_coef, precision, recall]
)

# INFO DO DATASET
print("="*60)
print("CONFIGURAÇÃO PARA 512x512 COM GPU POTENTE")
print("="*60)
print(f"Modelo: {model_name}")
print(f"Resolução: {input_dim_x}x{input_dim_y}")
print(f"Filtros base: {n_filters}")
print(f"Batch size: {batch_size}")
print(f"Epochs máximas: {epochs}")
print(f"Learning rate inicial: {initial_learning_rate}")
print(f"Loss function: Combined (10% BCE + 90% Dice)")
print(f"Early stopping patience: {early_stopping.patience}")

# Verificar dataset
train_samples = data_gen.get_num_data_points(train=True)
val_samples = data_gen.get_num_data_points(val=True)

print(f"Imagens de treino: {train_samples}")
print(f"Imagens de validação: {val_samples}")

if train_samples == 0:
    print("ERRO: Nenhum dado de treino encontrado!")
    print("Verifique se o dataset 'Foot_Ulcer_Segmentation_Challenge' existe em './data/'")
    exit(1)

# Calcular steps
steps_per_epoch = max(1, train_samples // batch_size)
validation_steps = max(1, val_samples // batch_size) if val_samples > 0 else 1

print(f"Steps per epoch: {steps_per_epoch}")
print(f"Validation steps: {validation_steps}")

# Estimar parâmetros do modelo
total_params = model.count_params()
print(f"Total de parâmetros: {total_params:,}")

# Estimar uso de memória GPU (aproximado)
memory_per_image = (input_dim_x * input_dim_y * 3 * 4) / (1024**2)  # MB por imagem
memory_estimate = memory_per_image * batch_size * 4  # Forward + backward + gradients
print(f"Uso estimado de GPU: ~{memory_estimate:.0f} MB por batch")
print("="*60)

# TREINAR
print("Iniciando treinamento...")
try:
    training_history = model.fit(
        data_gen.generate_data(batch_size=batch_size, train=True),
        steps_per_epoch=steps_per_epoch,
        callbacks=[early_stopping, reduce_lr, lr_scheduler],
        validation_data=data_gen.generate_data(batch_size=batch_size, val=True),
        validation_steps=validation_steps,
        epochs=epochs,
        verbose=1
    )
    
    # SALVAR MODELO E HISTÓRICO
    print("💾 Salvando modelo...")
    save_history(model, f'{model_name}_512x512_gpu', training_history, dataset, 
                 n_filters, epochs, initial_learning_rate, 'combined_loss', 
                 color_space='RGB', path='./training_history/')
    
    # ANÁLISE DOS RESULTADOS
    final_dice = training_history.history['val_dice_coef'][-1]
    best_dice = max(training_history.history['val_dice_coef'])
    best_epoch = training_history.history['val_dice_coef'].index(best_dice) + 1
    
    print("="*60)
    print("RELATÓRIO FINAL")
    print("="*60)
    print(f"Épocas treinadas: {len(training_history.history['loss'])}")
    print(f"Melhor época: {best_epoch}")
    print(f"Dice Score final: {final_dice:.4f}")
    print(f"Melhor Dice Score: {best_dice:.4f}")
    
    # Avaliação de qualidade
    if best_dice > 0.7:
        print("EXCELENTE! Modelo bem treinado")
    elif best_dice > 0.5:
        print("BOM! Modelo funcionando adequadamente")
    elif best_dice > 0.3:
        print("RAZOÁVEL - Considere mais épocas ou ajustes")
    elif best_dice > 0.1:
        print("NECESSITA AJUSTES - Modelo aprendendo mas precisa otimização")
    else:
        print("FALHA - Modelo não conseguiu aprender")
        print("Sugestões:")
        print("- Verificar se as labels estão corretas (0/1)")
        print("- Verificar correspondência imagem-label")
        print("- Considerar normalização diferente")
        print("- Verificar se dataset tem feridas suficientes")
    
    # Detectar overfitting
    final_train_dice = training_history.history['dice_coef'][-1]
    if final_train_dice - final_dice > 0.15:
        print("OVERFITTING detectado!")
        print("- Considere data augmentation")
        print("- Considere dropout maior")
        print("- Considere regularização L2")
        
except Exception as e:
    print(f"ERRO durante treinamento: {e}")
    import traceback
    traceback.print_exc()
    
    # Sugestões de debug
    print("\n🔍 Sugestões de debug:")
    print("1. Verificar se GPU tem memória suficiente")
    print("2. Tentar batch_size menor (4 ou 2)")
    print("3. Verificar paths dos dados")
    print("4. Verificar formato das imagens/labels")

print("="*60)
print("TREINAMENTO CONCLUÍDO!")
print("="*60)
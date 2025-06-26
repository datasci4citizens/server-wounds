from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import binary_crossentropy
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, LearningRateScheduler
from keras.models import load_model
from keras.utils.generic_utils import CustomObjectScope
import keras.backend as K

from models.unets import Unet2D
from models.deeplab import Deeplabv3, relu6, DepthwiseConv2D, BilinearUpsampling
from models.FCN import FCN_Vgg16_16s
from models.SegNet import SegNet

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
    # Pesos das loss functions (você pode ajustar)
    bce_weight = 0.50  # 50% Binary Crossentropy
    dice_weight = 0.50  # 50% Dice Loss
    
    # Calcular cada loss
    bce = binary_crossentropy(y_true, y_pred)
    dice = dice_coef_loss(y_true, y_pred)
    
    # Combinar
    return bce_weight * bce + dice_weight * dice

# LEARNING RATE SCHEDULER
def lr_schedule(epoch):
    """
    Reduz learning rate ao longo do tempo:
    - Épocas 0-150: 5e-5 (aprendizado inicial)
    - Épocas 150-400: 2e-5 (refinamento)
    - Épocas 400+: 1e-5 (ajuste fino)
    """
    return 1e-4

# PARÂMETROS OTIMIZADOS
input_dim_x = 512
input_dim_y = 512
n_filters = 16  # Modelo menor para evitar overfitting
dataset = 'Foot_Ulcer_Segmentation_Challenge'
data_gen = DataGen('./data/' + dataset + '/', split_ratio=0.2, x=input_dim_x, y=input_dim_y)

# MODELO U-NET
unet2d = Unet2D(n_filters=n_filters, input_dim_x=input_dim_x, input_dim_y=input_dim_y, num_channels=3)
model, model_name = unet2d.get_unet_model_yuanqing()

# HIPERPARÂMETROS DE TREINO
batch_size = 4
epochs = 100  
initial_learning_rate = 1e-4
loss_function = combined_loss

# CALLBACKS AVANÇADOS
# 1. EarlyStopping - para mais cedo se não melhorar
early_stopping = EarlyStopping(
    monitor='val_dice_coef',
    patience=3,  # ← AUMENTADO (era 50)
    mode='max',
    restore_best_weights=True,
    verbose=1,
    min_delta=0.001  # Melhoria mínima de 0.1%
)

# 2. ReduceLROnPlateau - reduz LR se estagnar
reduce_lr = ReduceLROnPlateau(
    monitor='val_dice_coef',
    factor=0.5,
    patience=5,  # Reduz LR se não melhorar por 30 épocas
    min_lr=1e-7,
    verbose=1
)

# 3. LearningRateScheduler - cronograma de LR
lr_scheduler = LearningRateScheduler(lr_schedule, verbose=1)

# COMPILAR MODELO
model.compile(
    optimizer=Adam(learning_rate=initial_learning_rate),
    loss=loss_function,  # ← COMBINED LOSS
    metrics=[dice_coef, precision, recall]
)

# INFO DO DATASET
print("="*50)
print("CONFIGURAÇÃO DO TREINO")
print("="*50)
print(f"Modelo: {model_name}")
print(f"Filtros: {n_filters}")
print(f"Batch size: {batch_size}")
print(f"Epochs máximas: {epochs}")
print(f"Learning rate inicial: {initial_learning_rate}")
print(f"Loss function: Combined (BCE + Dice)")
print(f"Imagens de treino: {data_gen.get_num_data_points(train=True)}")
print(f"Imagens de validação: {data_gen.get_num_data_points(val=True)}")
print("="*50)

# TREINAR
print("Iniciando treinamento...")
training_history = model.fit(
    data_gen.generate_data(batch_size=batch_size, train=True),
    steps_per_epoch=int(data_gen.get_num_data_points(train=True) / batch_size),
    callbacks=[early_stopping, reduce_lr, lr_scheduler],  # ← TODOS OS CALLBACKS
    validation_data=data_gen.generate_data(batch_size=batch_size, val=True),
    validation_steps=int(data_gen.get_num_data_points(val=True) / batch_size),
    epochs=epochs,
    verbose=1
)

# SALVAR MODELO E HISTÓRICO
print("Salvando modelo...")
save_history(model, model_name + '_combined_loss', training_history, dataset, 
             n_filters, epochs, initial_learning_rate, 'combined_loss', 
             color_space='RGB', path='./training_history/')

print("="*50)
print("TREINAMENTO CONCLUÍDO!")
print("="*50)
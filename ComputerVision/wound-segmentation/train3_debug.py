import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import binary_crossentropy
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, LearningRateScheduler
from tensorflow.keras.models import load_model, Model
import os
import numpy as np
import cv2
import datetime

from models.unets import Unet2D
from utils.learning.metrics import dice_coef, precision, recall
from utils.learning.losses import dice_coef_loss
from utils.io.data import DataGen

# DEBUGGING: Verificar dataset primeiro
def debug_dataset():
    print("🔍 DEBUGGING DATASET")
    print("=" * 40)
    
    dataset_path = './data/Medetec_foot_ulcer_224/'
    
    # Verificar estrutura
    train_imgs = dataset_path + 'train/images/'
    train_lbls = dataset_path + 'train/labels/'
    
    if not os.path.exists(train_imgs):
        print(f"❌ ERRO: {train_imgs} não existe!")
        return False
    
    if not os.path.exists(train_lbls):
        print(f"❌ ERRO: {train_lbls} não existe!")
        return False
    
    # Listar arquivos
    img_files = [f for f in os.listdir(train_imgs) if f.endswith('.png')]
    lbl_files = [f for f in os.listdir(train_lbls) if f.endswith('.png')]
    
    print(f"📁 Imagens: {len(img_files)}")
    print(f"📁 Labels: {len(lbl_files)}")
    
    if len(img_files) == 0:
        print("❌ ERRO: Nenhuma imagem encontrada!")
        return False
    
    # Testar primeira imagem
    img_path = os.path.join(train_imgs, img_files[0])
    lbl_path = os.path.join(train_lbls, lbl_files[0])
    
    img = cv2.imread(img_path)
    lbl = cv2.imread(lbl_path, 0)
    
    if img is None:
        print(f"❌ ERRO: Não foi possível ler {img_path}")
        return False
    
    if lbl is None:
        print(f"❌ ERRO: Não foi possível ler {lbl_path}")
        return False
    
    print(f"✅ Imagem shape: {img.shape}")
    print(f"✅ Label shape: {lbl.shape}")
    print(f"📊 Label min/max: {lbl.min()}/{lbl.max()}")
    print(f"📊 Label valores únicos: {np.unique(lbl)}")
    
    # Verificar pixels de ferida
    wound_pixels = np.sum(lbl > 127)  # Assumindo threshold 127
    total_pixels = lbl.size
    percentage = (wound_pixels / total_pixels) * 100
    
    print(f"🔍 Pixels de ferida: {wound_pixels}/{total_pixels} ({percentage:.2f}%)")
    
    if wound_pixels == 0:
        print("⚠️ AVISO: Nenhum pixel de ferida detectado!")
        print("💡 Verifique se as labels estão corretas")
        return False
    
    return True

# LOSS FUNCTION MAIS ROBUSTA
def robust_dice_loss(y_true, y_pred):
    """Dice loss mais robusta para casos extremos"""
    smooth = 1e-6
    
    # Flatten
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])
    
    # Intersection
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    
    # Dice
    dice = (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)
    
    return 1 - dice

def combined_loss_robust(y_true, y_pred):
    """Loss combinada mais robusta"""
    # Normalizar y_true para [0,1] se necessário
    y_true = tf.cast(y_true, tf.float32) / 255.0 if tf.reduce_max(y_true) > 1.0 else y_true
    
    bce = binary_crossentropy(y_true, y_pred)
    dice = robust_dice_loss(y_true, y_pred)
    
    return 0.3 * bce + 0.7 * dice

# VERIFICAR DATASET PRIMEIRO
if not debug_dataset():
    print("❌ Problema no dataset detectado!")
    exit(1)

print("\n🚀 INICIANDO TREINAMENTO CORRIGIDO")
print("=" * 50)

# PARÂMETROS CONSERVADORES
input_dim_x = 224
input_dim_y = 224
n_filters = 32  # Aumentado
dataset = 'Medetec_foot_ulcer_224'

# CRIAR DATA GENERATOR
data_gen = DataGen('./data/' + dataset + '/', split_ratio=0.2, x=input_dim_x, y=input_dim_y)

# Verificar dados carregados
train_samples = data_gen.get_num_data_points(train=True)
val_samples = data_gen.get_num_data_points(val=True)

print(f"📊 Amostras de treino: {train_samples}")
print(f"📊 Amostras de validação: {val_samples}")

if train_samples == 0:
    print("❌ ERRO: DataGen não carregou nenhuma amostra!")
    exit(1)

# MODELO U-NET
unet2d = Unet2D(n_filters=n_filters, input_dim_x=input_dim_x, input_dim_y=input_dim_y, num_channels=3)
model, model_name = unet2d.get_unet_model_yuanqing()

# HIPERPARÂMETROS CONSERVADORES
batch_size = 4  # Reduzido
epochs = 50     # Reduzido para teste
initial_learning_rate = 5e-4  # Mais conservador
loss_function = robust_dice_loss  # Loss mais robusta

# CALLBACKS MENOS AGRESSIVOS
early_stopping = EarlyStopping(
    monitor='val_dice_coef',
    patience=10,
    mode='max',
    restore_best_weights=True,
    verbose=1,
    min_delta=0.001
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_dice_coef',
    factor=0.5,
    patience=5,
    min_lr=1e-6,
    verbose=1,
    mode='max'
)

# COMPILAR MODELO
model.compile(
    optimizer=Adam(learning_rate=initial_learning_rate),
    loss=loss_function,
    metrics=[dice_coef, precision, recall]
)

print(f"📋 Configuração:")
print(f"  - Batch size: {batch_size}")
print(f"  - Learning rate: {initial_learning_rate}")
print(f"  - Epochs máx: {epochs}")
print(f"  - Loss: Dice robusta")

# TREINAR
print("\n🎯 Iniciando treinamento...")

try:
    # Testar um batch primeiro
    print("🧪 Testando um batch...")
    sample_batch = next(data_gen.generate_data(batch_size=2, train=True))
    print(f"  Batch shape: {sample_batch[0].shape}, {sample_batch[1].shape}")
    print(f"  Label min/max: {sample_batch[1].min():.3f}/{sample_batch[1].max():.3f}")
    
    # Treinar
    training_history = model.fit(
        data_gen.generate_data(batch_size=batch_size, train=True),
        steps_per_epoch=min(train_samples // batch_size, 20),  # Limitado para teste
        callbacks=[early_stopping, reduce_lr],
        validation_data=data_gen.generate_data(batch_size=batch_size, val=True),
        validation_steps=min(val_samples // batch_size, 5),
        epochs=epochs,
        verbose=1
    )
    
    # SALVAR MODELO SIMPLES
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    model_path = f"./training_history/model_debug_{timestamp}.keras"
    model.save(model_path)
    
    # SALVAR HISTÓRICO (COM CORREÇÃO JSON)
    history_data = {}
    for key, values in training_history.history.items():
        # Converter float32 para float
        history_data[key] = [float(v) for v in values]
    
    history_path = f"./training_history/history_debug_{timestamp}.json"
    import json
    with open(history_path, 'w') as f:
        json.dump(history_data, f, indent=2)
    
    # RELATÓRIO
    final_dice = training_history.history['val_dice_coef'][-1] if 'val_dice_coef' in training_history.history else 0
    best_dice = max(training_history.history['val_dice_coef']) if 'val_dice_coef' in training_history.history else 0
    
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO DE TREINAMENTO")
    print("=" * 50)
    print(f"🎯 Melhor Dice Score: {best_dice:.6f}")
    print(f"📈 Dice Score final: {final_dice:.6f}")
    print(f"📁 Modelo salvo: {model_path}")
    print(f"📁 Histórico salvo: {history_path}")
    
    if best_dice > 0.01:
        print("✅ Modelo começou a aprender!")
    else:
        print("⚠️ Modelo ainda não está aprendendo bem")
        print("💡 Verifique:")
        print("  - Labels estão corretas (0/1 ou 0/255)?")
        print("  - Há pixels de ferida suficientes?")
        print("  - Dataset está balanceado?")
    
except Exception as e:
    print(f"❌ ERRO durante treinamento: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)
print("✅ SCRIPT CONCLUÍDO")
print("=" * 50)
import os
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import binary_crossentropy
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, LearningRateScheduler, ModelCheckpoint
from tensorflow.keras.models import load_model, Model
import numpy as np
import datetime
import time

from models.unets import Unet2D
from utils.learning.metrics import dice_coef, precision, recall
from utils.learning.losses import dice_coef_loss
from utils.io.data import DataGen

# ========== CONFIGURAÇÃO GPU 0 ESPECÍFICA ==========
print("🔧 Configurando GPU 0 (RTX A5500)...")

# Forçar uso da GPU 0 especificamente
os.environ['CUDA_VISIBLE_DEVICES'] = '3'
os.environ['TF_GPU_ALLOCATOR'] = 'cuda_malloc_async'

# Configurar GPU
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        gpu = gpus[3]
        tf.config.experimental.set_device_policy('warn_on_error')
        tf.config.experimental.set_memory_growth(gpu, True)
        
        # Otimizações avançadas
        tf.config.optimizer.set_jit(True)  # XLA
        tf.config.optimizer.set_experimental_options({"layout_optimizer": True})
        
        print(f"✅ GPU 0 (RTX A5500) configurada - 24GB VRAM disponível")
    except RuntimeError as e:
        print(f"Erro na configuração: {e}")
else:
    print("❌ GPU não detectada")
    exit(1)

# Mixed Precision para 2x velocidade
from tensorflow.keras.mixed_precision import experimental as mixed_precision
policy = mixed_precision.Policy('mixed_float16')
mixed_precision.set_policy(policy)
print("✅ Mixed Precision (FP16) habilitado")

# ========== PARÂMETROS OTIMIZADOS PARA 256x256 + RTX A5500 ==========

# Dataset e dimensões
input_dim_x = 256
input_dim_y = 256
n_filters = 32              # ← Ótimo para 256x256 + 24GB VRAM
dataset = 'Foot_Ulcer_Segmentation_Challenge_256'

# Hiperparâmetros otimizados
batch_size = 16             # ← GRANDE (aproveitar 24GB VRAM)
epochs = 100                # Conforme solicitado
initial_learning_rate = 1e-3  # LR inicial moderado

print(f"📋 CONFIGURAÇÃO OTIMIZADA:")
print(f"  🖼️  Resolução: {input_dim_x}x{input_dim_y}")
print(f"  🔢 Filtros base: {n_filters}")
print(f"  📦 Batch size: {batch_size} (aproveitando 24GB)")
print(f"  🔄 Epochs máx: {epochs}")
print(f"  📈 LR inicial: {initial_learning_rate}")

# ========== FUNÇÕES DE LOSS OTIMIZADAS ==========

def optimized_dice_loss(y_true, y_pred):
    """Dice loss otimizada para FP16"""
    smooth = 1e-6
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    return 1 - (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)

def combined_loss_optimized(y_true, y_pred):
    """Loss combinada otimizada"""
    # Normalizar y_true se necessário
    y_true = tf.cast(y_true, tf.float32)
    if tf.reduce_max(y_true) > 1.0:
        y_true = y_true / 255.0
    
    bce = binary_crossentropy(y_true, y_pred)
    dice = optimized_dice_loss(y_true, y_pred)
    
    return 0.2 * bce + 0.8 * dice  # 80% Dice para segmentação

# ========== LEARNING RATE SCHEDULER PARA 100 ÉPOCAS ==========

def lr_schedule_100_epochs(epoch):
    """LR schedule otimizado para 100 épocas"""
    if epoch < 5:
        return 1e-3      # Início moderado
    elif epoch < 20:
        return 8e-4      # Redução gradual
    elif epoch < 40:
        return 5e-4      # LR médio
    elif epoch < 70:
        return 2e-4      # LR baixo
    else:
        return 1e-4      # LR final

# ========== VERIFICAR DATASET ==========

print("\n🔍 Verificando dataset...")
data_gen = DataGen('./data/' + dataset + '/', split_ratio=0.2, x=input_dim_x, y=input_dim_y)

train_samples = data_gen.get_num_data_points(train=True)
val_samples = data_gen.get_num_data_points(val=True)

print(f"📊 Amostras de treino: {train_samples}")
print(f"📊 Amostras de validação: {val_samples}")

if train_samples == 0:
    print("❌ ERRO: Dataset não encontrado!")
    print(f"💡 Certifique-se que existe: ./data/{dataset}/")
    print("💡 Execute primeiro: python resize_foot_ulcer_dataset.py com target_size=(256,256)")
    exit(1)

# Calcular steps
steps_per_epoch = max(1, train_samples // batch_size)
validation_steps = max(1, val_samples // batch_size) if val_samples > 0 else 1

print(f"🔄 Steps por época: {steps_per_epoch}")
print(f"✅ Steps validação: {validation_steps}")

# Estimativa de tempo
estimated_time_per_epoch = 2  # minutos para 256x256 + RTX A5500
total_estimated_time = estimated_time_per_epoch * epochs
print(f"⏰ Tempo estimado por época: ~{estimated_time_per_epoch} min")
print(f"⏰ Tempo total estimado: ~{total_estimated_time} min ({total_estimated_time/60:.1f}h)")

# ========== CRIAR MODELO ==========

print("\n🔧 Criando modelo U-Net...")
unet2d = Unet2D(n_filters=n_filters, input_dim_x=input_dim_x, input_dim_y=input_dim_y, num_channels=3)
model, model_name = unet2d.get_unet_model_yuanqing()

# ========== CALLBACKS OTIMIZADOS ==========

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
checkpoint_path = f"./training_history/checkpoint_256_{timestamp}.keras"

callbacks = [
    # Early stopping com paciência adequada para 100 épocas
    EarlyStopping(
        monitor='val_dice_coef',
        patience=20,        # 20% das épocas
        mode='max',
        restore_best_weights=True,
        verbose=1,
        min_delta=0.0005
    ),
    
    # Redução automática de LR
    ReduceLROnPlateau(
        monitor='val_dice_coef',
        factor=0.7,         # Redução suave
        patience=8,
        min_lr=5e-6,
        verbose=1,
        mode='max'
    ),
    
    # LR scheduler
    LearningRateScheduler(lr_schedule_100_epochs, verbose=1),
    
    # Checkpoint do melhor modelo
    ModelCheckpoint(
        filepath=checkpoint_path,
        monitor='val_dice_coef',
        save_best_only=True,
        mode='max',
        verbose=1
    )
]

# ========== COMPILAR COM MIXED PRECISION ==========

optimizer = Adam(learning_rate=initial_learning_rate)
optimizer = mixed_precision.LossScaleOptimizer(optimizer, loss_scale='dynamic')

model.compile(
    optimizer=optimizer,
    loss=combined_loss_optimized,
    metrics=[dice_coef, precision, recall]
)

print(f"\n📐 Arquitetura do modelo:")
print(f"  Parâmetros: {model.count_params():,}")

# Estimar uso de memória
memory_per_batch = (input_dim_x * input_dim_y * 3 * batch_size * 4) / (1024**2)  # MB
print(f"  Uso estimado VRAM: ~{memory_per_batch:.0f} MB por batch")

# ========== TREINAMENTO ==========

print("\n" + "="*60)
print("🚀 INICIANDO TREINAMENTO OTIMIZADO")
print("="*60)

# Warm up da GPU
print("🔥 Aquecendo GPU...")
dummy_batch = tf.random.normal((batch_size, input_dim_x, input_dim_y, 3))
_ = model(dummy_batch)
print("✅ GPU aquecida")

try:
    start_time = time.time()
    
    training_history = model.fit(
        data_gen.generate_data(batch_size=batch_size, train=True),
        steps_per_epoch=steps_per_epoch,
        callbacks=callbacks,
        validation_data=data_gen.generate_data(batch_size=batch_size, val=True),
        validation_steps=validation_steps,
        epochs=epochs,
        verbose=1,
        use_multiprocessing=True,
        workers=6,
        max_queue_size=20
    )
    
    end_time = time.time()
    total_time = (end_time - start_time) / 60  # minutos
    
    # ========== SALVAR RESULTADOS ==========
    
    print("\n💾 Salvando modelo e histórico...")
    
    # 1. Salvar modelo .keras (backup)
    final_model_path = f"./training_history/model_256_final_{timestamp}.keras"
    model.save(final_model_path)
    
    # 2. CRIAR MODELO COMPLETO PARA ONNX
    print("🔄 Criando modelo completo com pré/pós-processamento...")
    
    def create_onnx_ready_model(base_model):
        """Cria modelo completo para ONNX com processamento integrado"""
        from tensorflow.keras.layers import Input, Lambda
        
        # Input para qualquer tamanho de imagem
        input_layer = Input(shape=(None, None, 3), name='image_input', dtype=tf.uint8)
        
        # Pré-processamento integrado
        def preprocess(x):
            x = tf.cast(x, tf.float32)
            x = tf.image.resize(x, [input_dim_y, input_dim_x])
            x = x / 255.0
            return x
        
        # Pós-processamento integrado
        def postprocess(x):
            if len(x.shape) == 4 and x.shape[-1] > 1:
                x = x[:, :, :, 0]
            if len(x.shape) == 3:
                x = tf.expand_dims(x, -1)
            
            binary_mask = tf.cast(x > 0.5, tf.float32)
            pixel_count = tf.reduce_sum(binary_mask, axis=[1, 2, 3])
            
            return {
                'pixel_count': pixel_count,
                'binary_mask': binary_mask,
                'raw_prediction': x
            }
        
        # Pipeline completo
        preprocessed = Lambda(preprocess, name='preprocess')(input_layer)
        prediction = base_model(preprocessed)
        outputs = Lambda(postprocess, name='postprocess')(prediction)
        
        complete_model = Model(inputs=input_layer, outputs=outputs, name='WoundSegmentation256')
        return complete_model
    
    # Criar modelo completo
    complete_model = create_onnx_ready_model(model)
    
    # 3. SALVAR COMO SAVEDMODEL
    savedmodel_path = f"./training_history/savedmodel_256_{timestamp}"
    print(f"💾 Salvando SavedModel: {savedmodel_path}")
    
    @tf.function
    def serving_fn(image_input):
        return complete_model(image_input)
    
    # Criar signature para ONNX
    concrete_fn = serving_fn.get_concrete_function(
        tf.TensorSpec(shape=[1, None, None, 3], dtype=tf.uint8, name='image_input')
    )
    
    tf.saved_model.save(
        complete_model, 
        savedmodel_path, 
        signatures={'serving_default': concrete_fn}
    )
    
    # 4. EXPORTAR PARA ONNX
    onnx_path = f"./training_history/wound_segmentation_256_{timestamp}.onnx"
    print(f"🔄 Convertendo para ONNX: {onnx_path}")
    
    try:
        import tf2onnx
        
        # Comando de conversão
        conversion_cmd = f"python -m tf2onnx.convert --saved-model {savedmodel_path} --output {onnx_path} --opset 11"
        
        print("⚙️ Executando conversão ONNX...")
        result = os.system(conversion_cmd)
        
        if result == 0 and os.path.exists(onnx_path):
            print("✅ ONNX criado com sucesso!")
            
            # Verificar tamanho
            onnx_size = os.path.getsize(onnx_path) / (1024*1024)
            print(f"📊 Tamanho ONNX: {onnx_size:.1f} MB")
            
            # Criar script de uso ONNX
            onnx_usage_script = f'''# USO DO MODELO ONNX - UNIVERSAL!
import onnxruntime as ort
import cv2
import numpy as np

class WoundSegmentation256:
    def __init__(self, model_path="{onnx_path}"):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        print(f"✅ Modelo ONNX carregado: {{model_path}}")
    
    def count_pixels(self, image_path):
        """Conta pixels de ferida - FUNÇÃO PRINCIPAL"""
        # Ler imagem
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Erro lendo: {{image_path}}")
        
        # Converter BGR -> RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Adicionar batch dimension
        batch_image = np.expand_dims(image, axis=0).astype(np.uint8)
        
        # Executar inferência
        outputs = self.session.run(None, {{self.input_name: batch_image}})
        
        # Retornar contagem de pixels
        pixel_count = int(outputs[0][0])  # pixel_count é a primeira saída
        return pixel_count
    
    def get_mask(self, image_path):
        """Retorna máscara binária"""
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        batch_image = np.expand_dims(image, axis=0).astype(np.uint8)
        
        outputs = self.session.run(None, {{self.input_name: batch_image}})
        binary_mask = outputs[1][0]  # binary_mask é a segunda saída
        return binary_mask

# EXEMPLO DE USO:
if __name__ == "__main__":
    # Instalar: pip install onnxruntime opencv-python
    
    segmentator = WoundSegmentation256()
    
    # Contar pixels de ferida
    pixels = segmentator.count_pixels("sua_imagem.png")
    print(f"Pixels de ferida: {{pixels}}")
    
    # Obter máscara
    mask = segmentator.get_mask("sua_imagem.png")
    print(f"Máscara shape: {{mask.shape}}")
'''
            
            onnx_usage_path = f"./training_history/uso_onnx_256_{timestamp}.py"
            with open(onnx_usage_path, 'w') as f:
                f.write(onnx_usage_script)
            
            print(f"📝 Script de uso ONNX: {onnx_usage_path}")
            
        else:
            print("❌ Falha na conversão ONNX")
            print("💡 Instale tf2onnx: pip install tf2onnx")
            
    except ImportError:
        print("⚠️ tf2onnx não instalado!")
        print("📥 Para instalar: pip install tf2onnx")
        print(f"🔄 Para converter depois: python -m tf2onnx.convert --saved-model {savedmodel_path} --output {onnx_path}")
    
    # 5. Salvar histórico (com correção JSON)
    history_data = {}
    for key, values in training_history.history.items():
        history_data[key] = [float(v) for v in values]
    
    history_path = f"./training_history/history_256_{timestamp}.json"
    import json
    with open(history_path, 'w') as f:
        json.dump(history_data, f, indent=2)
    
    # ========== RELATÓRIO FINAL ==========
    
    epochs_trained = len(training_history.history['loss'])
    final_dice = training_history.history.get('val_dice_coef', [0])[-1]
    best_dice = max(training_history.history.get('val_dice_coef', [0]))
    best_epoch = training_history.history.get('val_dice_coef', [0]).index(best_dice) + 1
    avg_time_per_epoch = total_time / epochs_trained
    
    print("\n" + "="*60)
    print("🎉 TREINAMENTO CONCLUÍDO!")
    print("="*60)
    print(f"⏰ Tempo total: {total_time:.1f} min ({total_time/60:.1f}h)")
    print(f"⚡ Tempo médio por época: {avg_time_per_epoch:.1f} min")
    print(f"📊 Épocas treinadas: {epochs_trained}")
    print(f"🏆 Melhor época: {best_epoch}")
    print(f"🎯 Melhor Dice Score: {best_dice:.4f}")
    print(f"📈 Dice Score final: {final_dice:.4f}")
    
    # Avaliação de qualidade
    if best_dice > 0.8:
        print("🌟 EXCELENTE! Modelo muito bem treinado")
    elif best_dice > 0.7:
        print("🎉 MUITO BOM! Modelo bem treinado")
    elif best_dice > 0.5:
        print("✅ BOM! Modelo funcionando adequadamente")
    elif best_dice > 0.3:
        print("⚠️ RAZOÁVEL - Pode melhorar com mais épocas")
    else:
        print("🔧 NECESSITA AJUSTES - Verificar dados/hiperparâmetros")
    
    # Speedup real
    speedup_vs_512 = (512/256)**2  # Teórico
    actual_speedup = 30 / avg_time_per_epoch if avg_time_per_epoch > 0 else 0
    print(f"🚀 Speedup vs 512x512: ~{actual_speedup:.1f}x")
    
    print(f"\n📁 Arquivos salvos:")
    print(f"  🎯 MODELO PRINCIPAL: {onnx_path}")
    print(f"  🏆 Checkpoint: {checkpoint_path}")
    print(f"  💾 SavedModel: {savedmodel_path}")
    print(f"  📊 Modelo .keras: {final_model_path}")
    print(f"  📈 Histórico: {history_path}")
    if os.path.exists(onnx_path):
        print(f"  📝 Script uso ONNX: {onnx_usage_path}")
    
    print(f"\n🎯 MODELO PRINCIPAL PARA USO:")
    print(f"  Arquivo: {onnx_path}")
    print(f"  Formato: ONNX (universal)")
    print(f"  Funciona com: PyTorch, TensorFlow, C++, etc.")
    
    # Detectar overfitting
    final_train_dice = training_history.history.get('dice_coef', [0])[-1]
    if abs(final_train_dice - final_dice) > 0.1:
        print(f"\n⚠️ OVERFITTING detectado!")
        print(f"   Train Dice: {final_train_dice:.4f}")
        print(f"   Val Dice: {final_dice:.4f}")
        print(f"   Diferença: {abs(final_train_dice - final_dice):.4f}")
    
except Exception as e:
    print(f"❌ ERRO durante treinamento: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("🏁 SCRIPT CONCLUÍDO")
print("="*60)
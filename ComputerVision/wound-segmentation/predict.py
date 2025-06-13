import cv2
import os
from keras.models import load_model
from keras.utils.generic_utils import CustomObjectScope
from tensorflow.keras.losses import binary_crossentropy
import keras.backend as K

from models.unets import Unet2D
from models.deeplab import Deeplabv3, relu6, BilinearUpsampling, DepthwiseConv2D
from models.FCN import FCN_Vgg16_16s

from utils.learning.metrics import dice_coef, precision, recall
from utils.learning.losses import dice_coef_loss
from utils.BilinearUpSampling import BilinearUpSampling2D
from utils.io.data import load_data, save_results, save_rgb_results, save_history, load_test_images, DataGen

def combined_loss(y_true, y_pred):
    """
    Combina Binary Crossentropy + Dice Loss
    """
    bce_weight = 0.5
    dice_weight = 0.5
    
    bce = binary_crossentropy(y_true, y_pred)
    dice = dice_coef_loss(y_true, y_pred)
    
    return bce_weight * bce + dice_weight * dice

# settings
input_dim_x = 224
input_dim_y = 224
color_space = 'rgb'
path = './data/Medetec_foot_ulcer_224/'
weight_file_name = '2025-06-13 14:35:06.216528.hdf5'
pred_save_path = '2025-06-13 14:35:06.216528/'

# DEBUG: Verificar se as pastas existem
print(f"Verificando path: {path}")
print(f"Test images exist: {os.path.exists(path + 'test/images/')}")
print(f"Predictions dir exists: {os.path.exists(path + 'test/images/')}")

# Criar pasta de predições se não existir
os.makedirs(path + 'test/predictions/' + pred_save_path, exist_ok=True)
print(f"Created predictions dir: {path + 'test/predictions/' + pred_save_path}")

data_gen = DataGen(path, split_ratio=0.0, x=input_dim_x, y=input_dim_y, color_space=color_space)
x_test, test_label_filenames_list = load_test_images(path)

# DEBUG: Verificar imagens carregadas
print(f"Número de imagens de teste: {len(x_test) if x_test is not None else 0}")
print(f"Nomes dos arquivos: {test_label_filenames_list}")

# ### get unet model
unet2d = Unet2D(n_filters=16, input_dim_x=input_dim_x, input_dim_y=input_dim_y, num_channels=3)
model, model_name = unet2d.get_unet_model_yuanqing()
model = load_model('./training_history/' + weight_file_name
               , custom_objects={'recall':recall,
                                 'precision':precision,
                                 'dice_coef': dice_coef,
                                 'dice_coef_loss': dice_coef_loss,
                                 'combined_loss': combined_loss})

print("Modelo carregado com sucesso!")

for image_batch, label_batch in data_gen.generate_data(batch_size=len(x_test), test=True):
    print(f"Batch shape: {image_batch.shape}")
    prediction = model.predict(image_batch, verbose=1)
    print(f"Prediction shape: {prediction.shape}")
    print(f"Prediction min/max: {prediction.min():.4f}/{prediction.max():.4f}")
    
    # Salvar resultados
    save_results(prediction, 'rgb', path + 'test/predictions/' + pred_save_path, test_label_filenames_list)
    print(f"Tentando salvar em: {path + 'test/predictions/' + pred_save_path}")
    break

# Verificar se arquivos foram salvos
final_dir = path + 'test/predictions/' + pred_save_path
if os.path.exists(final_dir):
    files = os.listdir(final_dir)
    print(f"Arquivos salvos: {files}")
else:
    print("Diretório de predições não foi criado!")
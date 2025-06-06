import matplotlib.pyplot as plt
from skimage import io
from skimage.filters.rank import entropy
from skimage.morphology import disk
from skimage.color import rgb2gray
import numpy as np
from skimage.filters import threshold_otsu
import glob
import cv2

# Carrega a imagem
img = cv2.imread("images/group15.png")

# Cria o objeto de detecção de saliência
saliency = cv2.saliency.StaticSaliencyFineGrained_create()

# Calcula a saliência da imagem
(success, saliencyMap) = saliency.computeSaliency(img)
saliencyMap = (saliencyMap * 255).astype("uint8")

# Opcional: Aplica threshold para gerar uma máscara binária
(thresh, binaryMap) = cv2.threshold(saliencyMap, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# Salva ou exibe a máscara saliente
cv2.imwrite("saliency_map_group15.png", saliencyMap)
cv2.imwrite("binary_saliency_group15.png", binaryMap)
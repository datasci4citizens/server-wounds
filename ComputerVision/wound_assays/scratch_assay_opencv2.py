import cv2
import numpy as np

# Carrega a imagem
img = cv2.imread("images/group15.png")

# Reformata para um array 2D: cada linha é um pixel, cada coluna é uma característica (por exemplo, B, G, R)
pixels = img.reshape((-1, 3))
pixels = np.float32(pixels)

# Define critérios e número de clusters
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
K = 5  # Tente definir um número de clusters adequado ao caso
ret, labels, centers = cv2.kmeans(pixels, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

# Reorganiza os pixels de acordo com os clusters identificados
segmented = centers[labels.flatten()]
segmented_img = segmented.reshape(img.shape).astype(np.uint8)

cv2.imwrite("segmented_group15.png", segmented_img)

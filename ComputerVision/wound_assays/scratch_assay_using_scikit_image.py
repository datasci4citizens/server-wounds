import matplotlib.pyplot as plt
from skimage import io
from skimage.filters.rank import entropy
from skimage.morphology import disk
from skimage.color import rgb2gray
import numpy as np
from skimage.filters import threshold_otsu
import glob

img = io.imread("images/ankle3.jpg")
gray_img = rgb2gray(img)
gray_img = (gray_img * 255).astype(np.uint8)
entropy_img = entropy(gray_img, disk(5))
thresh = threshold_otsu(entropy_img)
binary = entropy_img <= thresh

plt.imsave("ankle_gray33.png", gray_img)
plt.imsave("ankle_entropy33.png", entropy_img)
plt.imsave("ankle_binary33.png", binary)
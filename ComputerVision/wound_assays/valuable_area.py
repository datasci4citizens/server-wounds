import cv2
import numpy as np

class ImgProcessor:
    def __init__(self, path, imName):
        self.path = path
        self.imName = imName
        self.original = cv2.imread(self.path+self.imName)

    def imProcess(self, ksmooth=7, kdilate=3, thlow=50, thigh= 100):
        # Read Image in BGR format
        img_bgr = self.original.copy()
        # Convert Image to Gray
        img_gray= cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        # Gaussian Filtering for Noise Removal
        gauss = cv2.GaussianBlur(img_gray, (ksmooth, ksmooth), 0)
        # Canny Edge Detection
        edges = cv2.Canny(gauss, thlow, thigh, 10)
        # Morphological Dilation
        # TODO: experiment diferent kernels
        kernel = np.ones((kdilate, kdilate), 'uint8')
        dil = cv2.dilate(edges, kernel)

        return dil
    
    def largestCC(self, imBW):
        # Extract Largest Connected Component
        # Source: https://stackoverflow.com/a/47057324
        image = imBW.astype('uint8')
        nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=4)
        sizes = stats[:, -1]

        max_label = 1
        max_size = sizes[1]
        for i in range(2, nb_components):
            if sizes[i] > max_size:
                max_label = i
                max_size = sizes[i]

        img2 = np.zeros(output.shape)
        img2[output == max_label] = 255
        return img2
    
    def maskCorners(self, mask, outval=1):
        y0 = np.min(np.nonzero(mask.sum(axis=1))[0])
        y1 = np.max(np.nonzero(mask.sum(axis=1))[0])
        x0 = np.min(np.nonzero(mask.sum(axis=0))[0])
        x1 = np.max(np.nonzero(mask.sum(axis=0))[0])
        output = np.zeros_like(mask)
        output[y0:y1, x0:x1] = outval
        return output

    def extractROI(self):
        im = self.imProcess()
        lgcc = self.largestCC(im)
        lgcc = lgcc.astype(np.uint8)
        roi = self.maskCorners(lgcc)
        # TODO mask BGR with this mask
        exroi = cv2.bitwise_and(self.original, self.original, mask = roi)
        return exroi

    def show_res(self):
        result = self.extractROI()
        cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
        cv2.imshow("Result", result)
        cv2.waitKey(0)

# ==============================================
if __name__ == "__main__":
    # TODO: change the path, and image name to suit your needs
    impr_ = ImgProcessor(path="/images/", imName="wound1.jpg")
    res = impr_.show_res()
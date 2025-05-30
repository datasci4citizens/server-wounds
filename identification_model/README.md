## Wound Tissue Type Classification with ResNet18 (wound_identification_supervised_model.py)
    This project implements a supervised image classification model using PyTorch to classify wound tissue types from images. It uses transfer learning with a pretrained ResNet-18 model to perform multi-class classification based on labeled wound images.

## Model Overview:
* Architecture: ResNet-18 (from torchvision)
* Modifications: Final fully-connected layer replaced to match number of wound tissue classes.
* Loss Function: Cross Entropy Loss
* Optimizer: Adam
* Learning Rate Scheduler: ReduceLROnPlateau (reduces learning rate if test loss plateaus)


## Techniques Used:
* Supervised Learning
    The model is trained on a labeled dataset where each image has a corresponding tissue type class.
* Transfer Learning
    Uses pretrained weights from ImageNet for ResNet-18 to speed up convergence and benefit from prior knowledge.
* Data Augmentation
    Improves generalization with:
        * Random horizontal flipping
        * Random rotation (±15°)
        * Normalization with ImageNet statistics
* Evaluation Metrics:
    Classification Report: Includes precision, recall, and F1-score for each class
    Confusion Matrix: Visualized with seaborn for better interpretability
* Learning Rate Scheduling:
    ReduceLROnPlateau adjusts the learning rate dynamically based on validation loss.
* Device Agnostic Training
    Automatically uses GPU (if available) or falls back to CPU.

## Running the model

Install Dependencies:

~~~ 
pip install torch torchvision pandas pillow scikit-learn matplotlib seaborn
~~~

Run the model:

~~~
python wound_identification_supervised_model.py
~~~

Ouput:
The best model is saved as wound_classifier_best.pth



## Image Class Balancer (balance_image_classes.py)
    This script is used to better distribute the image classes more equally between the 3 partitions(train, test, validation). The train partition gets at least 50% of the images from each class, and the other 50% is split between test and validation classes.

## CSV Analisys(csv_analisys.py)
    Just a simple script to study and get information from the classification, changed frequently according to what is the focus of the analisys.

## Image Labeler (label_images.py/exe)
    A program that allows the users to label the images at a fast pace. A image is show on the screen and a classification must be given, then it proceds to the next image that doesn't have a classification. The images he gets are from all_images folder and saves the results in labels.csv, ready to be used by the model.
* Dependencies:

~~~
pip install pillow pyinstaller
~~~

* Create the .exe

~~~
pyinstaller --onefile --noconsole --distpath . label_images.py
~~~

## Predict Single Image(predict_single_image.py)
    Uses the saved trained model to identify an image, outputing the predicted class. To change the predicted image, just change the image_path on main function to the name of image located in all_images.
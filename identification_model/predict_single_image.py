import torch
from torchvision import models, transforms
from PIL import Image
import pandas as pd
import os

def predict_image_class(image, model_path="wound_classifier_best.pth"):
    """
    Predict wound type from a PIL image or image path.

    Parameters:
    - image: str (file path) or PIL.Image.Image
    - model_path: path to the .pth file
    - label_csv_path: path to the CSV with class labels

    Returns:
    - predicted_label: str
    """

    # Load label mappings
    class_names = ["Epitelização", "Granulação", "Necrose", "Esfacelo", "NI"]  
    name_to_label = {name: idx for idx, name in enumerate(class_names)}
    label_to_name = {idx: name for name, idx in name_to_label.items()}

    # Preprocessing
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    # Open image if it's a path
    if isinstance(image, str):
        image_path = os.path.join("identification_model/all_images", image)
        image = Image.open(image_path).convert("RGB")

    elif not isinstance(image, Image.Image):
        raise TypeError("Input must be a PIL.Image.Image or path to image file")

    input_tensor = transform(image).unsqueeze(0)

    # Load model
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()

    with torch.no_grad():
        outputs = model(input_tensor)
        predicted_class = outputs.argmax(dim=1).item()

    predicted_label = label_to_name[predicted_class]
    return predicted_label

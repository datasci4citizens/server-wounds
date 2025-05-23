import torch
from torchvision import models, transforms
from PIL import Image
import pandas as pd
import sys
import os

def predict_image_class(img_path, model_path="wound_classifier_best.pth", label_csv_path="identification_model/labels.csv"):
    # Load label mappings
    img_path = "identification_model/validation/images/" + img_path
    df = pd.read_csv(label_csv_path)
    class_names = sorted(df["tissue_type"].unique())
    name_to_label = {name: idx for idx, name in enumerate(class_names)}
    label_to_name = {idx: name for name, idx in name_to_label.items()}

    # Preprocessing (must match training)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    # Load and preprocess image
    image = Image.open(img_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0)  # Shape: (1, 3, 224, 224)

    # Load model
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()

    # Predict
    with torch.no_grad():
        outputs = model(input_tensor)
        predicted_class = outputs.argmax(dim=1).item()

    predicted_label = label_to_name[predicted_class]
    return predicted_label

# Example usage (if run as script)
if __name__ == "__main__":
    image_path = "0009.png"
    label = predict_image_class(image_path)
    print(f"Tipo da ferida {image_path} identificado como: {label}")


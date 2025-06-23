import torch
from torchvision import models, transforms
from PIL import Image
import os
import torch.nn as nn

MODEL_DIR= os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(MODEL_DIR, "wound_classifier_best.pth")


def predict_image_class(image):
    """
    Predict wound type from a PIL image or image path.

    Parameters:
    - image: str (full file path) or PIL.Image.Image
    - model_path: path to the .pth file

    Returns:
    - predicted_label: str
    """
    MODEL_DIR= os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(MODEL_DIR, "wound_classifier_best.pth")
    class_names = ["Epitelização", "Granulação", "Necrose", "Esfacelo", "NI"]  
    label_to_name = {idx: name for idx, name in enumerate(class_names)}

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    if isinstance(image, str):
        image = Image.open(image).convert("RGB")
    elif not isinstance(image, Image.Image):
        raise TypeError("Input must be a PIL.Image.Image or path to image file")

    input_tensor = transform(image).unsqueeze(0)

    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
    model.load_state_dict(torch.load(model_path, map_location="cpu"), strict=False)
    model.eval()

    with torch.no_grad():
        outputs = model(input_tensor)
        predicted_class = outputs.argmax(dim=1).item()

    return label_to_name[predicted_class]


def predict_multi_label(image):
    """
    Predict W, I, Fi wound indicators from a PIL image or image path.

    Parameters:
    - image: str (full file path) or PIL.Image.Image
    - model_path: path to the .pth file

    Returns:
    - dict: {"W": int, "I": int, "Fi": int}
    """
    MODEL_DIR= os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(MODEL_DIR, "wound_classifier_best_multiclass.pth")
    if isinstance(image, str):
        image = Image.open(image).convert("RGB")
    elif not isinstance(image, Image.Image):
        raise TypeError("Input must be a PIL.Image.Image or path to image file")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])
    image_tensor = transform(image).unsqueeze(0).to(device)

    class MultiHeadResNet(nn.Module):
        def __init__(self, base_model, num_classes_per_label):
            super().__init__()
            self.features = nn.Sequential(*list(base_model.children())[:-1])
            in_features = base_model.fc.in_features
            self.fc_W = nn.Linear(in_features, num_classes_per_label)
            self.fc_I = nn.Linear(in_features, num_classes_per_label)
            self.fc_Fi = nn.Linear(in_features, num_classes_per_label)

        def forward(self, x):
            x = self.features(x)
            x = torch.flatten(x, 1)
            return self.fc_W(x), self.fc_I(x), self.fc_Fi(x)

    base_model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model = MultiHeadResNet(base_model, 4)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    with torch.no_grad():
        out_W, out_I, out_Fi = model(image_tensor)
        return {
            "W": torch.argmax(out_W, dim=1).item(),
            "I": torch.argmax(out_I, dim=1).item(),
            "Fi": torch.argmax(out_Fi, dim=1).item()
        }

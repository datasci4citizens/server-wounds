import torch
from torchvision import models, transforms
from PIL import Image
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



def predict_multi_label(image: Image.Image) -> dict:
    """
    Given a PIL image, predicts three wound-related labels (W, I, Fi)
    using a multi-head ResNet18 model.

    Returns:
        dict: {"W": int, "I": int, "Fi": int}
    """
    if not isinstance(image, Image.Image):
        raise TypeError("Input must be a PIL.Image.Image")

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Preprocessing
    eval_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])
    image_tensor = eval_transform(image).unsqueeze(0).to(device)

    # Model definition
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

    # Load model
    base_model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model = MultiHeadResNet(base_model, 4)
    model.load_state_dict(torch.load("wound_classifier_best_multiclass.pth", map_location=device))
    model.to(device)
    model.eval()

    # Predict
    with torch.no_grad():
        out_W, out_I, out_Fi = model(image_tensor)
        pred_W = torch.argmax(out_W, dim=1).item()
        pred_I = torch.argmax(out_I, dim=1).item()
        pred_Fi = torch.argmax(out_Fi, dim=1).item()

    return {
        "W": pred_W,
        "I": pred_I,
        "Fi": pred_Fi
    }

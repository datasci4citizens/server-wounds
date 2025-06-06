import os
import random
from PIL import Image
import torch
from torch import nn
from torchvision import models, transforms

# Model path (parent folder)
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wound_classifier_best_multiclass.pth")
ALL_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "all_images")

# Class names
class_names = ["W", "I", "Fi"]
class_labels = [0, 1, 2, 3]

# Image transform (same as eval_transform)
eval_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Model definition (must match training)
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
        out_W = self.fc_W(x)
        out_I = self.fc_I(x)
        out_Fi = self.fc_Fi(x)
        return out_W, out_I, out_Fi

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
base_model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model = MultiHeadResNet(base_model, 4)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()

# Pick a random image
image_files = [f for f in os.listdir(ALL_IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
if not image_files:
    print("No images found in all_images folder.")
    exit(1)
img_name = random.choice(image_files)
img_path = os.path.join(ALL_IMAGES_DIR, img_name)
print(f"Selected image: {img_name}")

# Load and preprocess image
image = Image.open(img_path).convert("RGB")
image_tensor = eval_transform(image).unsqueeze(0).to(device)

# Predict
with torch.no_grad():
    outputs_W, outputs_I, outputs_Fi = model(image_tensor)
    pred_W = torch.argmax(outputs_W, dim=1).item()
    pred_I = torch.argmax(outputs_I, dim=1).item()
    pred_Fi = torch.argmax(outputs_Fi, dim=1).item()

print("Predictions:")
print(f"W: {pred_W}")
print(f"I: {pred_I}")
print(f"Fi: {pred_Fi}")
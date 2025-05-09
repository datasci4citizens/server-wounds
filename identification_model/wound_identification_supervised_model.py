import os
import pandas as pd
from PIL import Image
import torch
from torch import nn
from torchvision import models, transforms
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Paths
train_img_dir = "identification_model/train/images"
val_img_dir = "identification_model/validation/images"
train_label_csv = "identification_model/train/predicted_wound_types.csv"
val_label_csv = "identification_model/validation/predicted_wound_types.csv"

# Load CSVs with tissue_type
train_label_df = pd.read_csv(train_label_csv)
val_label_df = pd.read_csv(val_label_csv)

# Create label encoder (str -> int)
classes = ['Granulation', 'Maceration', 'Slough', 'Necrotic']
label_to_idx = {label: idx for idx, label in enumerate(classes)}

# Map filenames to class indices
train_label_map = dict(zip(train_label_df['filename'], train_label_df['tissue_type'].map(label_to_idx)))
val_label_map = dict(zip(val_label_df['filename'], val_label_df['tissue_type'].map(label_to_idx)))

# Transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Custom Dataset
class WoundDataset(Dataset):
    def __init__(self, image_dir, label_map, transform=None):
        self.image_dir = image_dir
        self.image_files = sorted([
            f for f in os.listdir(image_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])
        self.label_map = label_map
        self.transform = transform

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_name = self.image_files[idx]
    
    # Skip files not in label map
        if img_name not in self.label_map:
            return self.__getitem__((idx + 1) % len(self))

        img_path = os.path.join(self.image_dir, img_name)
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        label = self.label_map[img_name]
        return image, label

# Load datasets
train_dataset = WoundDataset(train_img_dir, train_label_map, transform)
val_dataset = WoundDataset(val_img_dir, val_label_map, transform)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

# Model
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, 4)  # 4 classes
model = model.to("cpu")

# Training setup
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
epochs = 10

# Training loop
for epoch in range(epochs):
    model.train()
    running_loss = 0
    for imgs, labels in train_loader:
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    print(f"Epoch {epoch+1}/{epochs} - Loss: {running_loss:.4f}")

# Evaluation
model.eval()
y_true, y_pred = [], []
with torch.no_grad():
    for imgs, labels in val_loader:
        outputs = model(imgs)
        preds = outputs.argmax(dim=1).numpy()
        y_pred.extend(preds)
        y_true.extend(labels.numpy())

# Report
print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=classes))

# Confusion Matrix
conf = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(conf, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Confusion Matrix")
plt.show()

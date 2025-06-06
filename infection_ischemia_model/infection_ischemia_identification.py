import os
import pandas as pd
from PIL import Image
import torch
from torch import nn
from torchvision import models, transforms
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report
import numpy as np

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Paths
base_path = "infection_ischemia_model"
train_img_dir = os.path.join(base_path, "train")
val_img_dir = os.path.join(base_path, "validation")
test_img_dir = os.path.join(base_path, "test")
label_csv = os.path.join(base_path, "labels.csv")

# Load and prepare labels
df = pd.read_csv(label_csv)
df = df[["filename", "W", "I", "Fi"]]
class_names = ["W", "I", "Fi"]

# Normalize filenames
df["filename"] = df["filename"].str.strip().str.lower()
train_files = [f.lower() for f in os.listdir(train_img_dir)]
val_files = [f.lower() for f in os.listdir(val_img_dir)]
test_files = [f.lower() for f in os.listdir(test_img_dir)]

# Data splits
train_df = df[df['filename'].isin(train_files)]
val_df = df[df['filename'].isin(val_files)]
test_df = df[df['filename'].isin(test_files)]

train_label_map = {row['filename']: [int(row['W']), int(row['I']), int(row['Fi'])] for _, row in train_df.iterrows()}
val_label_map = {row['filename']: [int(row['W']), int(row['I']), int(row['Fi'])] for _, row in val_df.iterrows()}
test_label_map = {row['filename']: [int(row['W']), int(row['I']), int(row['Fi'])] for _, row in test_df.iterrows()}

# Transforms
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
eval_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Dataset
class WoundDataset(Dataset):
    def __init__(self, image_dir, label_map, transform):
        self.image_dir = image_dir
        self.image_files = sorted([
            f for f in os.listdir(image_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f.lower() in label_map
        ])
        self.label_map = label_map
        self.transform = transform

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_name = self.image_files[idx]
        img_path = os.path.join(self.image_dir, img_name)
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        # Each label is an integer (0-3)
        label = torch.tensor(self.label_map[img_name.lower()], dtype=torch.long)
        return image, label

# DataLoaders
train_dataset = WoundDataset(train_img_dir, train_label_map, train_transform)
val_dataset = WoundDataset(val_img_dir, val_label_map, eval_transform)
test_dataset = WoundDataset(test_img_dir, test_label_map, eval_transform)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

# Multi-head model for 3 outputs (W, I, Fi), each with 4 classes
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

model = MultiHeadResNet(models.resnet18(weights=models.ResNet18_Weights.DEFAULT), 4).to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, factor=0.5, patience=2)

# Training
best_val_loss = float('inf')
for epoch in range(10):
    model.train()
    running_loss = 0
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)
        outputs_W, outputs_I, outputs_Fi = model(imgs)
        loss_W = criterion(outputs_W, labels[:, 0])
        loss_I = criterion(outputs_I, labels[:, 1])
        loss_Fi = criterion(outputs_Fi, labels[:, 2])
        loss = loss_W + loss_I + loss_Fi
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    # Validation
    model.eval()
    val_loss = 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs_W, outputs_I, outputs_Fi = model(imgs)
            loss_W = criterion(outputs_W, labels[:, 0])
            loss_I = criterion(outputs_I, labels[:, 1])
            loss_Fi = criterion(outputs_Fi, labels[:, 2])
            loss = loss_W + loss_I + loss_Fi
            val_loss += loss.item()

    avg_val_loss = val_loss / len(val_loader)
    scheduler.step(avg_val_loss)
    print(f"Epoch {epoch+1}/10 - Train Loss: {running_loss:.4f} - Val Loss: {avg_val_loss:.4f}")

    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        torch.save(model.state_dict(), "wound_classifier_best_multiclass.pth")
        print("Saved best model.")

# Evaluation
model.load_state_dict(torch.load("wound_classifier_best_multiclass.pth"))
model.eval()
y_true = {l: [] for l in class_names}
y_pred = {l: [] for l in class_names}
with torch.no_grad():
    for imgs, labels in test_loader:
        imgs = imgs.to(device)
        outputs_W, outputs_I, outputs_Fi = model(imgs)
        preds_W = torch.argmax(outputs_W, dim=1).cpu().numpy()
        preds_I = torch.argmax(outputs_I, dim=1).cpu().numpy()
        preds_Fi = torch.argmax(outputs_Fi, dim=1).cpu().numpy()
        y_pred["W"].extend(preds_W)
        y_pred["I"].extend(preds_I)
        y_pred["Fi"].extend(preds_Fi)
        y_true["W"].extend(labels[:, 0].cpu().numpy())
        y_true["I"].extend(labels[:, 1].cpu().numpy())
        y_true["Fi"].extend(labels[:, 2].cpu().numpy())

from sklearn.metrics import classification_report

for label in class_names:
    print(f"\nClassification report for {label}:")
    report_dict = classification_report(
        y_true[label], y_pred[label],
        labels=[0, 1, 2, 3],
        target_names=[f"{label}=0", f"{label}=1", f"{label}=2", f"{label}=3"],
        zero_division=0,
        output_dict=True
    )
    df_report = pd.DataFrame(report_dict).transpose()
    print(df_report)

# Save predictions
predictions_df = pd.DataFrame({
    "filename": [test_dataset.image_files[i] for i in range(len(test_dataset))],
    "W": y_pred["W"],
    "I": y_pred["I"],
    "Fi": y_pred["Fi"]
})
output_csv_path = os.path.join(test_img_dir, "predicted_multiclass.csv")
predictions_df.to_csv(output_csv_path, index=False)
print(f"Predictions saved to '{output_csv_path}'")
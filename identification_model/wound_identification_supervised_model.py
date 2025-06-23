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

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Paths
train_img_dir = "identification_model/train/images"
test_img_dir = "identification_model/test/images"
label_csv = "identification_model/labels.csv"
save_model_path = os.path.join("citizens_project", "app_cicatrizando")

# Load string labels
df = pd.read_csv(label_csv)
class_names = sorted(df["tissue_type"].unique())
name_to_label = {name: idx for idx, name in enumerate(class_names)}
label_to_name = {idx: name for name, idx in name_to_label.items()}
df["label"] = df["tissue_type"].map(name_to_label)

train_df = df[df['filename'].isin(os.listdir(train_img_dir))]
test_df = df[df['filename'].isin(os.listdir(test_img_dir))]
train_label_map = dict(zip(train_df["filename"], train_df["label"]))
test_label_map = dict(zip(test_df["filename"], test_df["label"]))

# Transforms
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
test_transform = transforms.Compose([
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
            if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f in label_map
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
        label = self.label_map[img_name]
        return image, label

# DataLoaders
train_dataset = WoundDataset(train_img_dir, train_label_map, train_transform)
test_dataset = WoundDataset(test_img_dir, test_label_map, test_transform)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

# Model
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, len(class_names))
model = model.to(device)

# Training setup
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, factor=0.5, patience=2)

# Training loop with test loss tracking
best_test_loss = float('inf')
for epoch in range(10):
    model.train()
    running_loss = 0
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    model.eval()
    test_loss = 0
    with torch.no_grad():
        for imgs, labels in test_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            test_loss += loss.item()

    avg_test_loss = test_loss / len(test_loader)
    scheduler.step(avg_test_loss)
    print(f"Epoch {epoch+1}/10 - Train Loss: {running_loss:.4f} - Test Loss: {avg_test_loss:.4f}")

    if avg_test_loss < best_test_loss:
        best_test_loss = avg_test_loss
        torch.save(
    model.state_dict(),
    os.path.join(save_model_path, "wound_classifier_best.pth")
)
        print("Saved best model.")

# Final Evaluation on test set
model.load_state_dict(
    torch.load(os.path.join(save_model_path, "wound_classifier_best.pth"))
)
model.eval()
y_true, y_pred = [], []
with torch.no_grad():
    for imgs, labels in test_loader:
        imgs = imgs.to(device)
        outputs = model(imgs)
        preds = outputs.argmax(dim=1).cpu().numpy()
        y_pred.extend(preds)
        y_true.extend(labels.numpy())

print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=class_names, labels=list(range(len(class_names)))))


conf = confusion_matrix(y_true, y_pred, labels=list(range(len(class_names)))) 
plt.figure(figsize=(6, 5))
sns.heatmap(conf, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Confusion Matrix")
plt.show()

predictions_df = pd.DataFrame({
    "filename": [test_dataset.image_files[i] for i in range(len(test_dataset))],
    "true_label": [label_to_name[y] for y in y_true],
    "predicted_label": [label_to_name[y] for y in y_pred],
})
output_csv_path = "identification_model/test/predicted_classes.csv"
predictions_df.to_csv(output_csv_path, index=False)
print(f"Predictions saved to '{output_csv_path}'")
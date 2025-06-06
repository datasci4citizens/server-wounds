import os
import shutil
import pandas as pd
from collections import Counter

base_dir = "identification_model"
all_images_dir = os.path.join(base_dir, "all_images")

# --- STEP 1: Use local all_images folder ---
if not os.path.exists(all_images_dir):
    raise FileNotFoundError(f"Folder not found: {all_images_dir}")

# --- STEP 2: Balance and partition images ---
labels_path = os.path.join(base_dir, "labels.csv")
output_dirs = {
    "train": os.path.join(base_dir, "train", "images"),
    "test": os.path.join(base_dir, "test", "images"),
    "validation": os.path.join(base_dir, "validation", "images"),
}

for dir_path in output_dirs.values():
    os.makedirs(dir_path, exist_ok=True)
    # Clear existing images
    for f in os.listdir(dir_path):
        file_path = os.path.join(dir_path, f)
        if os.path.isfile(file_path):
            os.remove(file_path)

df = pd.read_csv(labels_path)
df = df[df["filename"].isin(os.listdir(all_images_dir))]
split_counts = {"train": [], "validation": [], "test": []}

for cls, group in df.groupby("tissue_type"):
    group = group.sample(frac=1, random_state=42)
    total = len(group)
    n_train = max(int(total * 0.60), 1)
    n_val_test = total - n_train
    n_val = n_test = n_val_test // 2
    if n_val_test % 2 != 0:
        n_val += 1

    train_files = group.iloc[:n_train]
    val_files = group.iloc[n_train:n_train + n_val]
    test_files = group.iloc[n_train + n_val:]

    for split, subset in zip(["train", "validation", "test"], [train_files, val_files, test_files]):
        for _, row in subset.iterrows():
            src = os.path.join(all_images_dir, row["filename"])
            dst = os.path.join(output_dirs[split], row["filename"])
            shutil.copyfile(src, dst)
            split_counts[split].append(row["tissue_type"])


# --- STEP 4: Report class counts ---
print("\n📊 Image Distribution Per Class:")
for split in ["train", "validation", "test"]:
    print(f"\n{split.upper()} SET:")
    counts = Counter(split_counts[split])
    for cls, count in sorted(counts.items()):
        print(f"{cls}: {count}")
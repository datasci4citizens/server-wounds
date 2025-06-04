import os
import shutil
import pandas as pd
from collections import Counter
import subprocess

def force_remove_readonly(func, path, excinfo):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

base_dir = "identification_model"
clone_path = os.path.join(base_dir, "all_images_temp")
all_images_dir = os.path.join(base_dir, "all_images")
repo_url = "https://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@github.com/JoaoCeleste/Wound_Images.git"

# --- STEP 1: Download all_images folder only if not present ---
if not os.path.exists(all_images_dir):
    if os.path.exists(clone_path):
        shutil.rmtree(clone_path, onerror=force_remove_readonly)

    subprocess.run(["git", "init", clone_path], check=True)
    subprocess.run(["git", "-C", clone_path, "remote", "add", "-f", "origin", repo_url], check=True)
    subprocess.run(["git", "-C", clone_path, "config", "core.sparseCheckout", "true"], check=True)

    sparse_file = os.path.join(clone_path, ".git", "info", "sparse-checkout")
    with open(sparse_file, "w") as f:
        f.write("all_images/\n")

    subprocess.run(["git", "-C", clone_path, "pull", "origin", "main"], check=True)

    all_images_src = os.path.join(clone_path, "all_images")
    if os.path.exists(all_images_dir):
        shutil.rmtree(all_images_dir, onerror=force_remove_readonly)
    shutil.move(all_images_src, all_images_dir)
    shutil.rmtree(clone_path, onerror=force_remove_readonly)

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
    n_train = max(int(total * 0.75), 1)
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

# --- STEP 3: Delete all_images ---
shutil.rmtree(all_images_dir, onerror=force_remove_readonly)

# --- STEP 4: Report class counts ---
print("\n📊 Image Distribution Per Class:")
for split in ["train", "validation", "test"]:
    print(f"\n{split.upper()} SET:")
    counts = Counter(split_counts[split])
    for cls, count in sorted(counts.items()):
        print(f"{cls}: {count}")
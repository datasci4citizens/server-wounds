import os
import shutil
import random
import pandas as pd

def split_dataset(train_ratio=0.75, val_ratio=0.15, test_ratio=0.10):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(base_dir, 'all_images')
    labels_path = os.path.join(base_dir, 'labels.csv')
    
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1"

    # Output folders
    train_dir = os.path.join(base_dir, 'train')
    val_dir = os.path.join(base_dir, 'validation')
    test_dir = os.path.join(base_dir, 'test')

    # Clear and create directories
    for directory in [train_dir, val_dir, test_dir]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory, exist_ok=True)

    # Load labels
    df = pd.read_csv(labels_path)
    valid_filenames = set(df['filename'].astype(str))

    # List all image files that have labels
    image_files = [f for f in os.listdir(source_dir)
                   if os.path.isfile(os.path.join(source_dir, f)) and f in valid_filenames]
    random.shuffle(image_files)

    total = len(image_files)
    train_end = int(train_ratio * total)
    val_end = train_end + int(val_ratio * total)

    # Split
    train_files = image_files[:train_end]
    val_files = image_files[train_end:val_end]
    test_files = image_files[val_end:]

    def copy_files(files, destination):
        for filename in files:
            src = os.path.join(source_dir, filename)
            dst = os.path.join(destination, filename)
            shutil.copy2(src, dst)

    copy_files(train_files, train_dir)
    copy_files(val_files, val_dir)
    copy_files(test_files, test_dir)

    print(f"Dataset split completed (only labeled images):")
    print(f"  Train: {len(train_files)} images")
    print(f"  Validation: {len(val_files)} images")
    print(f"  Test: {len(test_files)} images")

if __name__ == "__main__":
    split_dataset()
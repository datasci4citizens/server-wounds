import cv2
import numpy as np
import os
import csv
from sklearn.cluster import KMeans

def classify_wound_tissue(wound_pixels):
    # Convert to RGB
    pixels_rgb = cv2.cvtColor(wound_pixels, cv2.COLOR_BGR2RGB)

    # --- Stage 1: Necrotic detection ---
    hsv = cv2.cvtColor(wound_pixels, cv2.COLOR_BGR2HSV)
    brightness = hsv[:, :, 2]
    necrotic_mask = brightness < 40

    if np.count_nonzero(necrotic_mask) / necrotic_mask.size > 0.25:
        return "Necrotic"

    # --- Stage 2: Maceration detection ---
    saturation = hsv[:, :, 1]
    bright_mask = brightness > 180
    low_sat_mask = saturation < 50
    maceration_mask = bright_mask & low_sat_mask

    if np.count_nonzero(maceration_mask) / hsv.shape[0] / hsv.shape[1] > 0.15:
        return "Maceration"

    # --- Stage 3: KMeans clustering ---
    pixels = pixels_rgb.reshape(-1, 3)
    pixels = pixels[np.all(pixels > [40, 40, 40], axis=1)]  # remove very dark

    if len(pixels) == 0:
        return "Necrotic"

    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(pixels)
    dominant_colors = kmeans.cluster_centers_

    tissue_colors = {
        'Granulation': np.array([180, 60, 60]),
        'Maceration': np.array([240, 240, 230]),
        'Slough': np.array([210, 190, 120]),
        'Necrotic': np.array([30, 20, 10])
    }

    results = []
    for color in dominant_colors:
        distances = {
            tissue: np.linalg.norm(color - ref)
            for tissue, ref in tissue_colors.items()
        }
        results.append(min(distances, key=distances.get))

    return max(set(results), key=results.count) if results else "Necrotic"

# --- Main Script ---
if __name__ == "__main__":
    image_folder = "identification_model/validation/images"
    label_folder = "identification_model/validation/labels"
    output_csv = "identification_model/validation/predicted_wound_types.csv"

    if not os.path.exists(image_folder) or not os.path.exists(label_folder):
        print("Error: Missing 'train/images' or 'train/labels' directory.")
        exit()

    predictions = []

    for fname in sorted(os.listdir(image_folder)):
        if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, fname)
            mask_path = os.path.join(label_folder, fname)

            image = cv2.imread(image_path)
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

            if image is None or mask is None:
                print(f"Could not read {fname}. Skipping...")
                continue

            mask_bool = mask > 0
            wound_pixels = image[mask_bool]

            if wound_pixels.size == 0:
                print(f"No wound found in {fname}. Skipping.")
                continue

            wound_image = wound_pixels.reshape((-1, 1, 3))
            wound_image = np.ascontiguousarray(wound_image)

            tissue_type = classify_wound_tissue(wound_image)
            predictions.append((fname, tissue_type))
            print(f"{fname}: {tissue_type}")

    # Write CSV
    with open(output_csv, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'tissue_type'])
        writer.writerows(predictions)

    print(f"\n✅ Predictions saved to {output_csv}")

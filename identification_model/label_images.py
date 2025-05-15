import os
import csv
import tkinter as tk
from PIL import Image, ImageTk

# Settings
IMAGE_FOLDER = "all_images"
CSV_FILE = "labels.csv"
VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")

# Load existing labels
def load_existing_labels():
    if not os.path.exists(CSV_FILE):
        return {}
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        return {row[0]: row[1] for row in reader if len(row) == 2}

# Save label
def save_label(image_name, label):
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([image_name, label])

# GUI class
class ImageLabeler:
    def __init__(self, master, images_to_label):
        self.master = master
        self.images_to_label = images_to_label
        self.current_index = 0

        self.master.protocol("WM_DELETE_WINDOW", self.exit_program)  # Handle exit button
        self.master.title("Wound Labeler")

        self.label_var = tk.StringVar()
        self.image_label = tk.Label(self.master)
        self.image_label.pack()

        self.entry = tk.Entry(self.master, textvariable=self.label_var, font=("Arial", 16))
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.submit_label)

        self.load_image()

    def load_image(self):
        if self.current_index >= len(self.images_to_label):
            self.master.destroy()
            print("All images labeled.")
            return

        image_path = os.path.join(IMAGE_FOLDER, self.images_to_label[self.current_index])
        img = Image.open(image_path)
        img.thumbnail((800, 600))
        self.tk_img = ImageTk.PhotoImage(img)

        self.image_label.configure(image=self.tk_img)
        self.master.title(f"Classify: {self.images_to_label[self.current_index]}")
        self.label_var.set("")
        self.entry.focus_set()

    def submit_label(self, event=None):
        label = self.label_var.get().strip()
        if label:
            image_name = self.images_to_label[self.current_index]
            save_label(image_name, label)
            self.current_index += 1
            self.load_image()

    def exit_program(self):
        self.master.destroy()
        print("Exited by user.")

# Main execution
def main():
    existing_labels = load_existing_labels()
    all_images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(VALID_EXTENSIONS)]
    images_to_label = [img for img in all_images if img not in existing_labels]

    if not images_to_label:
        print("No images left to label.")
        return

    root = tk.Tk()
    app = ImageLabeler(root, images_to_label)
    root.mainloop()

if __name__ == "__main__":
    main()

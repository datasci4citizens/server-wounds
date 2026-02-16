import cv2
import numpy as np
from PIL import Image
import os

def get_reference_area(image_input):
    """
    Accepts either a file path or a PIL.Image.Image and returns the area of the detected reference pattern in pixels.
    Tries HoughCircles first, then fallback to contours.
    """
    # Handle different input types
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
        if img is None:
            raise ValueError(f"Could not load image from {image_input}")
    elif isinstance(image_input, Image.Image):
        img = cv2.cvtColor(np.array(image_input.convert("RGB")), cv2.COLOR_RGB2BGR)
    else:
        raise TypeError("image_input must be a file path (str) or PIL.Image.Image")

    original = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # Try HoughCircles first
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=100,
        param1=50,
        param2=30,
        minRadius=30,
        maxRadius=500
    )

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        best_circle = max(circles, key=lambda x: x[2])  # largest radius
        x, y, radius = best_circle
        return np.pi * (radius ** 2)

    # Fallback: Try contour detection
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter ** 2)
                if 0.6 < circularity < 1.4 and area > best_area:
                    best_area = area

    return best_area if best_area > 0 else None

#if __name__ == "__main__":
#    image = Image.open("ferida.png")
#    area = get_reference_area(image)
#    print("Detected area in pixels:", area)
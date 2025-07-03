import cv2
import numpy as np
from PIL import Image
import io

def calculate_reference_area(pil_image):
    """
    Calculate the area (in pixels) of the reference pattern in a PIL Image.
    
    Args:
        pil_image: PIL.Image.Image - Input image containing reference pattern
    
    Returns:
        float: Area of the detected reference pattern in pixels, or None if not detected
    """
    # Convert PIL Image to OpenCV format
    cv_image = pil_to_cv2(pil_image)
    
    # Detect the reference pattern
    result = detect_reference_circle_cv2(cv_image)
    
    if result:
        return result['area']
    return None

def pil_to_cv2(pil_image):
    """Convert PIL Image to OpenCV format"""
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Convert bytes to numpy array and then to OpenCV format
    np_arr = np.frombuffer(img_byte_arr, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

def detect_reference_circle_cv2(cv_image):
    """Detect reference circle in OpenCV format image"""
    # Preprocessing
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    processed = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Try contour detection first
    result = detect_by_contours(processed)
    if result:
        return result
    
    # Fallback to Hough Circles if contour fails
    return detect_by_hough(processed)

def detect_by_contours(processed_img):
    """Contour-based detection with area calculation"""
    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(processed_img, 255, 
                                  cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 11, 2)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 
                                  cv2.CHAIN_APPROX_SIMPLE)
    
    best_circle = None
    best_score = 0
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:  # Minimum area threshold
            continue
            
        perimeter = cv2.arcLength(cnt, True)
        circularity = 4 * np.pi * area / (perimeter**2) if perimeter > 0 else 0
        
        (x,y), radius = cv2.minEnclosingCircle(cnt)
        compactness = area / (np.pi * radius**2) if radius > 0 else 0
        
        # Score combines multiple factors
        score = (circularity * 0.6 + compactness * 0.4) * min(1, radius/50)
        
        if score > best_score and circularity > 0.7:
            best_score = score
            best_circle = {
                'center': (int(x), int(y)),
                'radius': int(radius),
                'area': np.pi * radius**2,  # Area in pixels
                'circularity': circularity,
                'score': score
            }
    
    return best_circle

def detect_by_hough(processed_img):
    """Hough Circle detection with area calculation"""
    # Edge detection
    edges = cv2.Canny(processed_img, 50, 150)
    
    # Hough Circle detection
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1.2, 
                              minDist=100,
                              param1=50, param2=30,
                              minRadius=20, maxRadius=300)
    
    if circles is not None:
        circles = np.uint16(np.around(circles[0]))
        # Select circle with strongest response
        x, y, r = circles[0]
        return {
            'center': (x, y),
            'radius': r,
            'area': np.pi * r**2,  # Area in pixels
            'score': 0.8  # Default confidence
        }
    return None


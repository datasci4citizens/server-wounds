import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_reference_circle(image_path):
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not loaded")
    
    # Preprocessing (using bilateral filter as you indicated it works best)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Multiple detection approaches
    methods = [
        ("Contour", detect_by_contours(processed)),
        ("Hough", detect_by_hough(processed)),
        ("Template", detect_by_template(processed))
    ]
    
    # Evaluate results and pick best
    best_result = None
    best_score = 0
    
    for name, result in methods:
        if result and result['score'] > best_score:
            best_result = result
            best_result['method'] = name
            best_score = result['score']
    
    # Visualization
    if best_result:
        visualize_results(img, processed, best_result)
        return best_result
    else:
        print("No pattern detected")
        return None

def detect_by_contours(processed_img):
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
        if area < 500:  # Adjust based on expected size
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
                'area': np.pi * radius**2,
                'circularity': circularity,
                'score': score
            }
    
    return best_circle

def detect_by_hough(processed_img):
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
            'area': np.pi * r**2,
            'score': 0.8  # Default confidence
        }
    return None

def detect_by_template(processed_img):
    # Create synthetic template (adjust based on your pattern)
    template = np.zeros((100, 100), dtype=np.uint8)
    cv2.circle(template, (50, 50), 45, 255, 2)
    
    # Match template
    res = cv2.matchTemplate(processed_img, template, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(res)
    
    # Estimate circle parameters
    x, y = max_loc[0] + 50, max_loc[1] + 50  # Template center
    return {
        'center': (x, y),
        'radius': 45,
        'area': np.pi * 45**2,
        'score': 0.7  # Default confidence
    }

def visualize_results(original, processed, result):
    plt.figure(figsize=(15,5))
    
    # Original image
    plt.subplot(1,3,1)
    plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    plt.title("Original Image")
    plt.axis('off')
    
    # Processed image
    plt.subplot(1,3,2)
    plt.imshow(processed, cmap='gray')
    plt.title("Processed Image")
    plt.axis('off')
    
    # Detection result
    detected_img = original.copy()
    cv2.circle(detected_img, result['center'], result['radius'], (0,255,0), 2)
    cv2.circle(detected_img, result['center'], 2, (0,0,255), 3)
    
    plt.subplot(1,3,3)
    plt.imshow(cv2.cvtColor(detected_img, cv2.COLOR_BGR2RGB))
    plt.title(f"Detected (Method: {result['method']})\n"
              f"Radius: {result['radius']}px\n"
              f"Score: {result['score']:.2f}")
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

# Usage
detect_reference_circle("ferida4.jpg")
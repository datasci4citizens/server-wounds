import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_reference_pattern(image_path):
    """
    Detect the circular reference pattern and return its area in pixels
    """
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    original = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # Use HoughCircles to detect circular patterns
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
        
        # Find the circle with the most defined pattern (best score)
        best_circle = circles[0]  # Start with first detected circle
        
        # If multiple circles detected, you might want to choose the largest one
        # or implement additional logic to select the reference pattern
        if len(circles) > 1:
            # Choose the largest circle as it's likely the main reference
            best_circle = max(circles, key=lambda x: x[2])
        
        x, y, radius = best_circle
        
        # Calculate area in pixels
        area_pixels = np.pi * (radius ** 2)
        
        # Draw the detected circle for visualization
        cv2.circle(img, (x, y), radius, (0, 255, 0), 2)
        cv2.circle(img, (x, y), 2, (0, 0, 255), 3)
        
        return {
            'center': (x, y),
            'radius': radius,
            'area_pixels': area_pixels,
            'detected_image': img,
            'original_image': original
        }
    
    return None

def detect_reference_by_contours(image_path):
    """
    Alternative method: Detect reference pattern using contour detection
    """
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    original = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to get binary image
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    best_circle = None
    best_area = 0
    
    for contour in contours:
        # Calculate area
        area = cv2.contourArea(contour)
        
        # Filter by area (adjust these values based on your image)
        if area > 1000:  # Minimum area threshold
            # Check if contour is roughly circular
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # If circularity is close to 1, it's likely a circle
                if 0.6 < circularity < 1.4 and area > best_area:
                    # Fit a circle to the contour
                    (x, y), radius = cv2.minEnclosingCircle(contour)
                    
                    best_circle = {
                        'center': (int(x), int(y)),
                        'radius': int(radius),
                        'area_pixels': area,
                        'circularity': circularity
                    }
                    best_area = area
    
    if best_circle:
        x, y = best_circle['center']
        radius = best_circle['radius']
        
        # Draw the detected circle
        cv2.circle(img, (x, y), radius, (0, 255, 0), 2)
        cv2.circle(img, (x, y), 2, (0, 0, 255), 3)
        
        best_circle['detected_image'] = img
        best_circle['original_image'] = original
        
        return best_circle
    
    return None

def main():
    # Update this with your image path
    image_path = "ferida.png"  # Change this to your image path
    
    try:
        print("Detecting reference pattern using Hough Circles...")
        result_hough = detect_reference_pattern(image_path)
        
        print("Detecting reference pattern using Contours...")
        result_contour = detect_reference_by_contours(image_path)
        
        # Display results
        if result_hough:
            x, y = result_hough['center']
            radius = result_hough['radius']
            area = result_hough['area_pixels']
            
            print(f"\n=== HOUGH CIRCLES METHOD ===")
            print(f"Reference pattern detected!")
            print(f"Center: ({x}, {y})")
            print(f"Radius: {radius} pixels")
            print(f"Area: {area:.2f} pixels")
            print(f"Diameter: {radius * 2} pixels")
        else:
            print("Reference pattern not detected with Hough Circles method")
        
        if result_contour:
            x, y = result_contour['center']
            radius = result_contour['radius']
            area = result_contour['area_pixels']
            circularity = result_contour['circularity']
            
            print(f"\n=== CONTOURS METHOD ===")
            print(f"Reference pattern detected!")
            print(f"Center: ({x}, {y})")
            print(f"Radius: {radius} pixels")
            print(f"Area: {area:.2f} pixels")
            print(f"Diameter: {radius * 2} pixels")
            print(f"Circularity: {circularity:.3f}")
        else:
            print("Reference pattern not detected with Contours method")
        
        # Visualize results
        plt.figure(figsize=(15, 5))
        
        if result_hough:
            plt.subplot(1, 3, 1)
            plt.imshow(cv2.cvtColor(result_hough['original_image'], cv2.COLOR_BGR2RGB))
            plt.title("Original Image")
            plt.axis('off')
            
            plt.subplot(1, 3, 2)
            plt.imshow(cv2.cvtColor(result_hough['detected_image'], cv2.COLOR_BGR2RGB))
            plt.title(f"Hough Circles\nArea: {result_hough['area_pixels']:.0f} pixels")
            plt.axis('off')
        
        if result_contour:
            plt.subplot(1, 3, 3)
            plt.imshow(cv2.cvtColor(result_contour['detected_image'], cv2.COLOR_BGR2RGB))
            plt.title(f"Contours Method\nArea: {result_contour['area_pixels']:.0f} pixels")
            plt.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        # Return the best result
        if result_hough and result_contour:
            # You can choose which method to prefer
            print(f"\nBoth methods detected the pattern.")
            print(f"Choose the result that looks more accurate in the visualization.")
            return result_hough  # or return result_contour
        elif result_hough:
            return result_hough
        elif result_contour:
            return result_contour
        else:
            print("Could not detect reference pattern with either method.")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to:")
        print("1. Install required packages: pip install opencv-python matplotlib numpy")
        print("2. Update the image_path variable with your actual file path")
        return None

def get_reference_area(image_path):
    """
    Simple function that just returns the area in pixels
    """
    result = detect_reference_pattern(image_path)
    if result:
        return result['area_pixels']
    
    # Try alternative method
    result = detect_reference_by_contours(image_path)
    if result:
        return result['area_pixels']
    
    return None

if __name__ == "__main__":
    # Example usage
    result = main()
    
    if result:
        print(f"\nFinal Result: {result['area_pixels']:.2f} pixels")
    
    # Or use the simple function directly:
    # area = get_reference_area("your_image.jpg")
    # if area:
    #     print(f"Reference area: {area:.2f} pixels")
import cv2
import numpy as np
import math

def detect_calibration_circle(image):
    """
    Detecta o círculo de calibração preto na imagem.
    
    Args:
        image: Imagem onde detectar o círculo
    
    Returns:
        area_pixels: Área do círculo em pixels
        circle_info: Tupla (x, y, raio) do círculo detectado
    """
    # Converte para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Cria máscara para pixels muito escuros (círculo preto)
    _, black_mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)
    
    # Encontra contornos
    contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Procura por contorno circular
    best_circle = None
    best_circularity = 0
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 100:  # Ignora contornos muito pequenos
            continue
            
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
            
        # Calcula circularidade (1.0 = círculo perfeito)
        circularity = 4 * math.pi * area / (perimeter * perimeter)
        
        # Verifica se é aproximadamente circular
        if circularity > 0.7 and circularity > best_circularity:
            best_circularity = circularity
            best_circle = contour
            
    if best_circle is not None:
        # Calcula centro e raio
        (x, y), radius = cv2.minEnclosingCircle(best_circle)
        area_pixels = cv2.contourArea(best_circle)
        
        print(f"Círculo de calibração detectado:")
        print(f"  Centro: ({int(x)}, {int(y)})")
        print(f"  Raio: {radius:.1f} pixels")
        print(f"  Área: {area_pixels:.0f} pixels")
        print(f"  Circularidade: {best_circularity:.2f}")
        
        return area_pixels, (int(x), int(y), int(radius))
    else:
        print("AVISO: Círculo de calibração não detectado!")
        return None, None

def calculate_scale_factor(circle_area_pixels, real_radius_cm):
    """
    Calcula o fator de escala baseado no círculo de referência.
    
    Args:
        circle_area_pixels: Área do círculo em pixels
        real_radius_cm: Raio real do círculo em cm
    
    Returns:
        scale_factor: Fator para converter pixels² em cm²
    """
    # Área real do círculo em cm²
    real_area_cm2 = math.pi * (real_radius_cm ** 2)
    
    # Fator de escala: cm²/pixel²
    scale_factor = real_area_cm2 / circle_area_pixels
    
    # Calcula também pixels por cm (útil para referência)
    pixels_per_cm = math.sqrt(circle_area_pixels / real_area_cm2)
    
    print(f"\nCálculo da escala:")
    print(f"  Área real do círculo: {real_area_cm2:.2f} cm²")
    print(f"  Área em pixels: {circle_area_pixels:.0f} pixels")
    print(f"  Fator de escala: 1 pixel² = {scale_factor:.6f} cm²")
    print(f"  Resolução: {pixels_per_cm:.1f} pixels/cm")
    
    return scale_factor

def calculate_wound_area_with_scale(segmented_img_path, target_color_hex="#2B0E0D", 
                                   reference_radius_cm=2.7):
    """
    Calcula a área da ferida em pixels e cm² usando círculo de referência.
    
    Args:
        segmented_img_path: Caminho para a imagem segmentada
        target_color_hex: Cor alvo em formato hexadecimal
        reference_radius_cm: Raio real do círculo de referência em cm
    
    Returns:
        dict: Dicionário com todas as medições
    """
    # Carrega a imagem segmentada
    segmented_img = cv2.imread(segmented_img_path)
    
    # Detecta o círculo de calibração
    circle_area_pixels, circle_info = detect_calibration_circle(segmented_img)
    
    if circle_area_pixels is None:
        print("Erro: Não foi possível detectar o círculo de calibração!")
        print("Continuando sem conversão para cm²...")
        scale_factor = None
    else:
        scale_factor = calculate_scale_factor(circle_area_pixels, reference_radius_cm)
    
    # Converte cor hex para BGR
    hex_color = target_color_hex.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    bgr_target = (rgb[2], rgb[1], rgb[0])
    
    # Obtém cores únicas na imagem
    pixels = segmented_img.reshape(-1, 3)
    unique_colors = np.unique(pixels, axis=0)
    
    #print(f"\nCores únicas encontradas na imagem segmentada:")
    for i, color in enumerate(unique_colors):
        rgb_color = (color[2], color[1], color[0])
        hex_found = '#{:02x}{:02x}{:02x}'.format(rgb_color[0], rgb_color[1], rgb_color[2])
    
    # Encontra a cor mais próxima da cor alvo
    distances = []
    for color in unique_colors:
        dist = np.linalg.norm(color - np.array(bgr_target))
        distances.append(dist)
    
    closest_idx = np.argmin(distances)
    closest_color = unique_colors[closest_idx]
    
    print(f"\nCor mais próxima de {target_color_hex}: BGR{tuple(closest_color)}")
    
    # Cria máscara para a cor mais próxima
    mask = cv2.inRange(segmented_img, closest_color, closest_color)
    
    # Remove o círculo de calibração da máscara se detectado
    if circle_info is not None:
        x, y, r = circle_info
        cv2.circle(mask, (x, y), r + 5, 0, -1)  # Remove círculo + margem
    
    # Calcula a área
    area_pixels = cv2.countNonZero(mask)
    
    # Calcula a porcentagem
    total_pixels = segmented_img.shape[0] * segmented_img.shape[1]
    percentage = (area_pixels / total_pixels) * 100
    
    # Calcula área em cm² se temos a escala
    area_cm2 = area_pixels * scale_factor if scale_factor else None
    
    return {
        'area_pixels': area_pixels,
        'area_cm2': area_cm2,
        'percentage': percentage,
        'mask': mask,
        'scale_factor': scale_factor,
        'circle_info': circle_info
    }

def visualize_results_with_scale(original_path, segmented_path, results):
    """
    Visualiza os resultados incluindo a escala.
    """
    # Carrega as imagens
    original = cv2.imread(original_path)
    segmented = cv2.imread(segmented_path)
    
    # Cria visualização com contornos
    contours, _ = cv2.findContours(results['mask'], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Copia a imagem original
    result = original.copy()
    cv2.drawContours(result, contours, -1, (0, 255, 0), 2)
    
    # Marca o círculo de calibração se detectado
    if results['circle_info'] is not None:
        x, y, r = results['circle_info']
        cv2.circle(result, (x, y), r, (255, 0, 0), 2)
        cv2.putText(result, "Ref: 2.7cm", (x - 40, y - r - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
    
    # Adiciona texto com informações
    font = cv2.FONT_HERSHEY_SIMPLEX
    y_pos = 30
    
    # Informações básicas
    text1 = f"Area: {results['area_pixels']} px ({results['percentage']:.1f}%)"
    cv2.putText(result, text1, (10, y_pos), font, 0.7, (0, 255, 0), 2)
    
    # Área em cm² se disponível
    if results['area_cm2'] is not None:
        y_pos += 30
        text2 = f"Area: {results['area_cm2']:.2f} cm²"
        cv2.putText(result, text2, (10, y_pos), font, 0.7, (0, 255, 0), 2)
        
        # Adiciona barra de escala
        pixels_per_cm = 1.0 / math.sqrt(results['scale_factor'])
        scale_bar_length = int(pixels_per_cm)  # 1 cm
        scale_bar_start = (result.shape[1] - scale_bar_length - 20, result.shape[0] - 30)
        scale_bar_end = (result.shape[1] - 20, result.shape[0] - 30)
        
        cv2.line(result, scale_bar_start, scale_bar_end, (0, 0, 0), 5)
        cv2.line(result, scale_bar_start, scale_bar_end, (255, 255, 255), 3)
        cv2.putText(result, "1 cm", (scale_bar_start[0] - 10, scale_bar_start[1] - 5),
                   font, 0.5, (0, 0, 0), 2)
        cv2.putText(result, "1 cm", (scale_bar_start[0] - 10, scale_bar_start[1] - 5),
                   font, 0.5, (255, 255, 255), 1)
    
    # Salva as visualizações
    cv2.imwrite("wound_mask_calibrated.png", results['mask'])
    cv2.imwrite("wound_analysis_calibrated.png", result)
    
    # Cria comparação
    comparison = np.hstack([original, segmented, cv2.cvtColor(results['mask'], cv2.COLOR_GRAY2BGR)])
    cv2.imwrite("wound_comparison_calibrated.png", comparison)
    
    print(f"\nResultados salvos:")
    print(f"  - wound_mask_calibrated.png: Máscara binária da ferida")
    print(f"  - wound_analysis_calibrated.png: Resultado com medidas")
    print(f"  - wound_comparison_calibrated.png: Comparação lado a lado")

# Código principal
if __name__ == "__main__":

    img = cv2.imread("images/ankle2.jpg")

    # Calcula a área da ferida com calibração
    print("\nCalculando área da ferida com calibração...")
    results = calculate_wound_area_with_scale("images/ankle_coin2.png", 
                                            target_color_hex="#2B0E0D",
                                            reference_radius_cm=2.7)
    
    print(f"\n{'='*50}")
    print(f"RESULTADOS FINAIS")
    print(f"{'='*50}")
    print(f"Área da ferida:")
    print(f"  - Em pixels: {results['area_pixels']} pixels")
    print(f"  - Porcentagem: {results['percentage']:.2f}%")
    
    if results['area_cm2'] is not None:
        print(f"  - Em cm²: {results['area_cm2']:.2f} cm²")
        
        # Calcula dimensões aproximadas
        area_mm2 = results['area_cm2'] * 100
        print(f"  - Em mm²: {area_mm2:.0f} mm²")
        
        # Estima diâmetro se fosse circular
        diameter_cm = 2 * math.sqrt(results['area_cm2'] / math.pi)
        print(f"  - Diâmetro equivalente: {diameter_cm:.1f} cm")
    else:
        print("\nNOTA: Para obter medidas em cm², certifique-se de que:")
        print("  1. O círculo de referência está visível na imagem")
        print("  2. O círculo é preto e bem definido")
        print("  3. O círculo tem 2.7 cm de raio na vida real")
    
    print(f"\nDimensões da imagem: {img.shape[1]} x {img.shape[0]} pixels")
    
    # Visualiza os resultados
    visualize_results_with_scale("images/ankle2.jpg", "images/ankle_coin2.png", results)
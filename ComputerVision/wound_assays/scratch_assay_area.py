import cv2
import numpy as np

def hex_to_bgr(hex_color):
    """Converte cor hexadecimal para BGR (formato OpenCV)"""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])  # BGR

def find_color_area(image_path, target_hex):
    """
    Calcula a área de uma cor específica na imagem.
    
    Args:
        image_path: Caminho da imagem segmentada
        target_hex: Cor em formato hexadecimal (ex: "#2B0E0D")
    
    Returns:
        dict: Dicionário com área, porcentagem e informações adicionais
    """
    # Carrega a imagem
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    total_pixels = height * width
    
    # Converte hex para BGR
    target_bgr = hex_to_bgr(target_hex)
    
    # Encontra todas as cores únicas na imagem
    pixels = img.reshape(-1, 3)
    unique_colors = np.unique(pixels, axis=0)
    
    # Encontra a cor mais próxima do alvo
    min_distance = float('inf')
    closest_color = None
    
    for color in unique_colors:
        distance = np.sqrt(np.sum((color - target_bgr) ** 2))
        if distance < min_distance:
            min_distance = distance
            closest_color = color
    
    # Cria máscara para a cor encontrada
    mask = np.all(img == closest_color, axis=2)
    
    # Calcula área
    area_pixels = np.sum(mask)
    percentage = (area_pixels / total_pixels) * 100
    
    # Converte a cor encontrada para hex para mostrar
    found_rgb = (closest_color[2], closest_color[1], closest_color[0])
    found_hex = '#{:02x}{:02x}{:02x}'.format(found_rgb[0], found_rgb[1], found_rgb[2])
    
    return {
        'area_pixels': area_pixels,
        'percentage': percentage,
        'total_pixels': total_pixels,
        'image_dimensions': (width, height),
        'target_color': target_hex,
        'found_color': found_hex,
        'mask': mask.astype(np.uint8) * 255
    }

# Exemplo de uso
if __name__ == "__main__":
    # Analisa a área da cor escura (ferida)
    result = find_color_area("images/segmented_ankle2.png", "#2B0E0D")
    
    print("=== ANÁLISE DA ÁREA DA FERIDA ===")
    print(f"Cor procurada: {result['target_color']}")
    print(f"Cor mais próxima encontrada: {result['found_color']}")
    print(f"Área: {result['area_pixels']} pixels")
    print(f"Porcentagem da imagem: {result['percentage']:.2f}%")
    print(f"Dimensões da imagem: {result['image_dimensions'][0]} x {result['image_dimensions'][1]}")
    
    # Salva a máscara
    # Analisa todas as três cores mencionadas
    print("\n=== ANÁLISE DE TODAS AS CORES ===")
    cores = ["#2B0E0D", "#905954", "#B38379"]
    
    for cor in cores:
        r = find_color_area("images/segmented_ankle2.png", cor)
        print(f"\nCor {cor}:")
        print(f"  Área: {r['area_pixels']} pixels ({r['percentage']:.1f}%)")
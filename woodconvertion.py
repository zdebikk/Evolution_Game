import numpy as np
from PIL import Image, ImageEnhance

def get_tree_density_grid(image_path, cols, rows, contrast_level=4.0):
    img = Image.open(image_path)
    
    # NEW: Apply contrast enhancement
    # 1.0 is the original image. Values > 1.0 increase contrast.
    # 3.0 heavily separates the dark trees from the light fields.
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast_level)
    
    # 1. Resize image to exactly match your grid size
    img = img.resize((cols, rows))
    
    # 2. Convert to grayscale
    gray_img = img.convert('L')
    
    # 3. Convert to numpy array and transpose to match (cols, rows)
    intensity_matrix = np.array(gray_img).T
    
    # 4. Invert intensity for weights and ensure uint8 dtype
    tree_weights = (255 - intensity_matrix).astype(np.uint8)
    
    return tree_weights

if __name__ == "__main__":
    COLS = int(1900/4)
    ROWS = int(1600/4)
    
    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
    tree_grid = get_tree_density_grid("map.png", COLS, ROWS)
    t_cols, t_rows = tree_grid.shape

    grid[:t_cols, :t_rows] = grid[:t_cols, :t_rows] + tree_grid
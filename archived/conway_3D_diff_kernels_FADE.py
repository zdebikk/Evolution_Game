import pygame
import numpy as np
from scipy.signal import convolve2d

# --- 1. Dimensions & Resolution ---
COLS = 300
ROWS = 175
CELL_SIZE = 4
WIDTH_PX = COLS * CELL_SIZE
HEIGHT_PX = ROWS * CELL_SIZE
PROBABILITY_ALIVE = 0.15  # Probability that a cell starts alive

# --- 2. Configuration & RGB Mapping ---
CHANNEL_CONFIG = {
    'R': 1,
    'G': 2,
    'B': 3 
}

# The amount subtracted from pixel brightness every frame (higher = faster fade)
FADE_SPEED = 8.0 

KERNELS = {
    1: np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]]),
    2: np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]),
    3: np.array([[1, 2, 1], [2, 0, 2], [1, 2, 1]]),
    4: np.array([[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 0, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1]])
}

def apply_rule(layer, mode):
    kernel = KERNELS[mode]
    neighbors = convolve2d(layer, kernel, mode='same', boundary='wrap')
    
    if mode == 1:
        return ((neighbors == 3) | ((layer == 1) & (neighbors == 2))).astype(np.uint8)
    elif mode == 2:
        return ((neighbors == 1) | ((layer == 1) & (neighbors == 2))).astype(np.uint8)
    elif mode == 3:
        return (((neighbors == 5) | (neighbors == 6)) | 
                ((layer == 1) & ((neighbors >= 4) & (neighbors <= 7)))).astype(np.uint8)
    elif mode == 4:
        return (((neighbors >= 7) & (neighbors <= 9)) | 
                ((layer == 1) & ((neighbors >= 5) & (neighbors <= 7)))).astype(np.uint8)

def init_grids():
    base_seed = np.random.choice([0, 1], size=(COLS, ROWS), p=[1-PROBABILITY_ALIVE, PROBABILITY_ALIVE]).astype(np.uint8)
    return np.array([base_seed.copy(), base_seed.copy(), base_seed.copy()])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    pygame.display.set_caption(f"RGB Automaton - R:Mode{CHANNEL_CONFIG['R']} | G:Mode{CHANNEL_CONFIG['G']} | B:Mode{CHANNEL_CONFIG['B']} (SPACE to run)")
    clock = pygame.time.Clock()

    grids = init_grids()
    
    # The visual display array uses floats to allow smooth subtraction over time
    display_rgb = np.zeros((COLS, ROWS, 3), dtype=np.float32)

    modes = [CHANNEL_CONFIG['R'], CHANNEL_CONFIG['G'], CHANNEL_CONFIG['B']]
    running = True
    paused = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grids = init_grids()
                    display_rgb.fill(0) # Clear the trails instantly on reset
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_c:
                    grids = np.zeros((3, COLS, ROWS), dtype=np.uint8)
                    display_rgb.fill(0)

        # --- Mouse Drawing Logic ---
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] or mouse_buttons[2]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = mouse_x // CELL_SIZE
            grid_y = mouse_y // CELL_SIZE
            
            if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                if mouse_buttons[0]:
                    grids[:, grid_x, grid_y] = 1
                elif mouse_buttons[2]:
                    grids[:, grid_x, grid_y] = 0
                    # Also instantly erase the visual trail where the user right-clicks
                    display_rgb[grid_x, grid_y, :] = 0 

        # --- Compute Next Generation ---
        if not paused:
            for i in range(3):
                grids[i] = apply_rule(grids[i], modes[i])
            
            # Subtract fade speed from all current visual pixels
            display_rgb -= FADE_SPEED
            # Prevent values from dropping below 0
            np.clip(display_rgb, 0, 255, out=display_rgb)

        # --- Render RGB Image ---
        # Map the current binary grid to 255
        current_active = (np.transpose(grids, (1, 2, 0)) * 255).astype(np.float32)
        
        # Override faded pixels with maximum brightness wherever a cell is currently alive
        display_rgb = np.maximum(display_rgb, current_active)

        # Convert back to standard 8-bit integers for Pygame rendering
        rgb_array = display_rgb.astype(np.uint8)

        surface = pygame.surfarray.make_surface(rgb_array)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else 30)

    pygame.quit()

if __name__ == "__main__":
    main()
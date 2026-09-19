import pygame
import numpy as np
from scipy.signal import convolve2d

# --- 1. Dimensions & Resolution ---
COLS = 300
ROWS = 175
CELL_SIZE = 4
WIDTH_PX = COLS * CELL_SIZE
HEIGHT_PX = ROWS * CELL_SIZE

# --- 2. Configuration & Visuals ---
FADE_SPEED = 8.0 
BG_COLOR = np.array([18, 18, 24], dtype=np.float32)

# Standard Conway Kernel used for all channels
KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])

def apply_conway(layer):
    """Applies the standard B3/S23 Game of Life rule."""
    neighbors = convolve2d(layer, KERNEL, mode='same', boundary='wrap')
    return ((neighbors == 3) | ((layer == 1) & (neighbors == 2))).astype(np.uint8)

def init_grids():
    """Initializes three distinct grids with different spawn probabilities."""
    # Red starts sparse (P=0.1)
    r_seed = np.random.choice([0, 1], size=(COLS, ROWS), p=[0.9, 0.1]).astype(np.uint8)
    
    # Green starts moderate (P=0.3)
    g_seed = np.random.choice([0, 1], size=(COLS, ROWS), p=[0.7, 0.3]).astype(np.uint8)
    
    # Blue starts dense (P=0.5)
    b_seed = np.random.choice([0, 1], size=(COLS, ROWS), p=[0.5, 0.5]).astype(np.uint8)
    
    return np.array([r_seed, g_seed, b_seed])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    grids = init_grids()
    display_rgb = np.full((COLS, ROWS, 3), BG_COLOR, dtype=np.float32)

    running = True
    paused = True
    fade_enabled = True  # Fading starts turned on

    def update_caption():
        status = "Running" if not paused else "Paused"
        fade_status = "ON" if fade_enabled else "OFF"
        pygame.display.set_caption(f"RGB Conway [{status}] | Fade: {fade_status} (Press F) | SPACE to play")

    update_caption()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grids = init_grids()
                    display_rgb[:, :] = BG_COLOR
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    update_caption()
                elif event.key == pygame.K_c:
                    grids = np.zeros((3, COLS, ROWS), dtype=np.uint8)
                    display_rgb[:, :] = BG_COLOR
                # --- Toggle Fading Logic ---
                elif event.key == pygame.K_f:
                    fade_enabled = not fade_enabled
                    update_caption()

        # --- Mouse Drawing Logic ---
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] or mouse_buttons[2]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = mouse_x // CELL_SIZE
            grid_y = mouse_y // CELL_SIZE
            
            if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                # Drawing injects life into all 3 probability dimensions simultaneously
                if mouse_buttons[0]:
                    grids[:, grid_x, grid_y] = 1
                elif mouse_buttons[2]:
                    grids[:, grid_x, grid_y] = 0
                    display_rgb[grid_x, grid_y, :] = BG_COLOR 

        # --- Compute Next Generation ---
        if not paused:
            for i in range(3):
                grids[i] = apply_conway(grids[i])
        
        # --- Visuals Processing ---
        if fade_enabled:
            if not paused:
                # Subtract fade speed and clamp to background color
                display_rgb -= FADE_SPEED
                display_rgb = np.maximum(display_rgb, BG_COLOR)
        else:
            # If fading is off, instantly wipe the screen to the background color every frame
            display_rgb[:, :] = BG_COLOR

        # --- Render RGB Image ---
        # Map living cells to 255 for vibrant color blending
        current_active = (np.transpose(grids, (1, 2, 0)) * 255).astype(np.float32)
        display_rgb = np.maximum(display_rgb, current_active)

        rgb_array = display_rgb.astype(np.uint8)
        surface = pygame.surfarray.make_surface(rgb_array)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else 30)

    pygame.quit()

if __name__ == "__main__":
    main()
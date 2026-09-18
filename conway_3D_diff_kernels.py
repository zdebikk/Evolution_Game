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
# Assign which mode (1 to 4) runs on which color channel
CHANNEL_CONFIG = {
    'R': 1,
    'G': 3,
    'B': 4,
}

# --- 3. Spatial Awareness Kernels ---
KERNELS = {
    1: np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]]),
    2: np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]),
    3: np.array([[1, 2, 1], [2, 0, 2], [1, 2, 1]]),
    4: np.array([[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 0, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1]])
}

def apply_rule(layer, mode):
    """Applies the specific spatial awareness rule to a single 2D layer."""
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
    """Generates an identical starting seed for all three layers to allow fair comparison."""
    base_seed = np.random.choice([0, 1], size=(COLS, ROWS), p=[1-PROBABILITY_ALIVE, PROBABILITY_ALIVE]).astype(np.uint8)
    # Stack 3 identical copies so every species starts from the exact same layout
    return np.array([base_seed.copy(), base_seed.copy(), base_seed.copy()])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    # Update title to show channel assignments
    pygame.display.set_caption(f"RGB Automaton - R:Mode{CHANNEL_CONFIG['R']} | G:Mode{CHANNEL_CONFIG['G']} | B:Mode{CHANNEL_CONFIG['B']} (SPACE to run)")
    clock = pygame.time.Clock()

    # grids is now a 3D array: Shape (3, COLS, ROWS) representing (Channel, X, Y)
    grids = init_grids()  # Start with a random canvas for all channels
    #grids = np.zeros((3, COLS, ROWS), dtype=np.uint8)
    
    # Map the dictionary config to a list we can iterate over [Red_mode, Green_mode, Blue_mode]
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
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_c:
                    grids = np.zeros((3, COLS, ROWS), dtype=np.uint8) # Press 'C' to clear

        # --- Mouse Drawing Logic ---
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] or mouse_buttons[2]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = mouse_x // CELL_SIZE
            grid_y = mouse_y // CELL_SIZE
            
            if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                # [:, x, y] targets the same coordinate across all 3 color channels instantly
                if mouse_buttons[0]:
                    grids[:, grid_x, grid_y] = 1
                elif mouse_buttons[2]:
                    grids[:, grid_x, grid_y] = 0

        # --- Compute Next Generation ---
        if not paused:
            # Process each color channel individually through its assigned rule
            for i in range(3):
                grids[i] = apply_rule(grids[i], modes[i])

        # --- Render RGB Image ---
        # 1. Transpose the axes from (Channels, X, Y) to (X, Y, Channels) which Pygame expects
        # 2. Multiply by 255 to map our binary 0s and 1s to standard 8-bit RGB values
        rgb_array = (np.transpose(grids, (1, 2, 0)) * 255).astype(np.uint8)

        surface = pygame.surfarray.make_surface(rgb_array)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else 30)

    pygame.quit()

if __name__ == "__main__":
    main()
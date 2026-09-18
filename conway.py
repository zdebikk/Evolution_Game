import pygame
import numpy as np
from scipy.signal import convolve2d

# --- 1. Dimensions & Resolution ---
COLS = 300       # Number of logical cells horizontally
ROWS = 175       # Number of logical cells vertically
CELL_SIZE = 4    # Each cell renders as a 4x4 pixel block

# The window resolution is now calculated dynamically based on the grid
WIDTH_PX = COLS * CELL_SIZE
HEIGHT_PX = ROWS * CELL_SIZE

# --- 2. Visuals ---
# Pygame expects RGB colors. 
BG_COLOR = np.array([18, 18, 24])        # Dark slate background
ALIVE_COLOR = np.array([0, 255, 170])    # Neon mint for living cells

# --- 3. Core Engine ---
KERNEL = np.array([[1, 1, 1],
                   [1, 0, 1],
                   [1, 1, 1]])

def init_grid():
    # Initialize the asymmetric grid with a 15% chance of a cell being alive
    return np.random.choice([0, 1], size=(COLS, ROWS), p=[0.85, 0.15])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    pygame.display.set_caption("Game of Life - Vectorized Animation")
    clock = pygame.time.Clock()

    grid = init_grid()
    
    # Pre-allocate an RGB array to translate the 0s and 1s into pixel data
    # Pygame's surfarray natively expects a (width, height, 3) configuration
    rgb_array = np.zeros((COLS, ROWS, 3), dtype=np.uint8)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                grid = init_grid()  # Press 'R' to randomize and restart the animation

        # --- Phase 1: Compute Next Generation ---
        neighbors = convolve2d(grid, KERNEL, mode='same', boundary='wrap')
        # Apply B3/S23 rules. The bitwise operators keep this entirely in C.
        grid = ((neighbors == 3) | ((grid == 1) & (neighbors == 2))).astype(np.uint8)

        # --- Phase 2: Render Animation ---
        # Map the binary states to the pre-allocated color arrays
        rgb_array[grid == 0] = BG_COLOR
        rgb_array[grid == 1] = ALIVE_COLOR

        # Instantly convert the raw NumPy RGB array into a renderable Pygame Surface
        surface = pygame.surfarray.make_surface(rgb_array)
        
        # Scale the small logical surface up to fill the exact pixel dimensions of the window
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        # Draw and update the frame
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        
        # Cap at 30 FPS so you can actually watch the patterns evolve
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
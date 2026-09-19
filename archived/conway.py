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

# --- 2. Visuals ---
BG_COLOR = np.array([18, 18, 24])
ALIVE_COLOR = np.array([0, 255, 170])

# --- 3. Core Engine ---
KERNEL = np.array([[1, 1, 1],
                   [1, 0, 1],
                   [1, 1, 1]])

def init_grid():
    return np.random.choice([0, 1], size=(COLS, ROWS), p=[1-PROBABILITY_ALIVE, PROBABILITY_ALIVE])

def main():
    pygame.init() 
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    pygame.display.set_caption("Game of Life - Paused (Press SPACE to run)")
    clock = pygame.time.Clock()


    grid = init_grid()  # Start with a random canvas
    #grid = np.zeros((COLS, ROWS), dtype=np.uint8) # Start with a blank canvas
    rgb_array = np.zeros((COLS, ROWS, 3), dtype=np.uint8)

    running = True
    paused = True  # Simulation starts paused

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grid = init_grid()
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    caption = "Game of Life - Running" if not paused else "Game of Life - Paused"
                    pygame.display.set_caption(caption)

        # --- Mouse Drawing Logic ---
        # 0: Left Click (Draw), 2: Right Click (Erase)
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] or mouse_buttons[2]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # Map window pixels back to logical grid coordinates
            grid_x = mouse_x // CELL_SIZE
            grid_y = mouse_y // CELL_SIZE
            
            # Boundary check to prevent errors if the mouse drags outside the window
            if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                if mouse_buttons[0]:
                    grid[grid_x, grid_y] = 1
                elif mouse_buttons[2]:
                    grid[grid_x, grid_y] = 0

        # --- Phase 1: Compute Next Generation ---
        if not paused:
            neighbors = convolve2d(grid, KERNEL, mode='same', boundary='wrap')
            grid = ((neighbors == 3) | ((grid == 1) & (neighbors == 2))).astype(np.uint8)

        # --- Phase 2: Render Animation ---
        rgb_array[grid == 0] = BG_COLOR
        rgb_array[grid == 1] = ALIVE_COLOR

        surface = pygame.surfarray.make_surface(rgb_array)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        
        # Boost framerate while paused for smoother mouse drawing
        clock.tick(60 if paused else 30)

    pygame.quit()

if __name__ == "__main__":
    main()
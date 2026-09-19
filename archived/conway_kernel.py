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

# --- 3. Spatial Awareness Kernels ---
KERNEL_1 = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]]) # Standard Moore
KERNEL_2 = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]) # Von Neumann
KERNEL_3 = np.array([[1, 2, 1], [2, 0, 2], [1, 2, 1]]) # Weighted Proximity
KERNEL_4 = np.ones((5, 5), dtype=int)
KERNEL_4[2, 2] = 0 # 5x5 Macro

def init_grid():
    return np.random.choice([0, 1], size=(COLS, ROWS), p=[1-PROBABILITY_ALIVE, PROBABILITY_ALIVE])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()



    grid = init_grid()  # Start with a random canvas
    #grid = np.zeros((COLS, ROWS), dtype=np.uint8) # Start with a blank canvas
    rgb_array = np.zeros((COLS, ROWS, 3), dtype=np.uint8)

    running = True
    paused = True
    current_mode = 1
    
    # Helper function to dynamically update the window title
    def update_caption():
        status = "Running" if not paused else "Paused"
        modes = {
            1: "Standard Conway (B3/S23)", 
            2: "Von Neumann Fractals", 
            3: "Weighted Amoebas", 
            4: "5x5 Macro Islands"
        }
        pygame.display.set_caption(f"[{status}] Mode {current_mode}: {modes[current_mode]} | Press 1-4 to switch")

    update_caption()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grid = init_grid()
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    update_caption()
                # --- Mode Switching Logic ---
                elif event.key == pygame.K_1:
                    current_mode = 1; update_caption()
                elif event.key == pygame.K_2:
                    current_mode = 2; update_caption()
                elif event.key == pygame.K_3:
                    current_mode = 3; update_caption()
                elif event.key == pygame.K_4:
                    current_mode = 4; update_caption()

        # --- Mouse Drawing Logic ---
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] or mouse_buttons[2]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = mouse_x // CELL_SIZE
            grid_y = mouse_y // CELL_SIZE
            
            if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
                if mouse_buttons[0]: grid[grid_x, grid_y] = 1
                elif mouse_buttons[2]: grid[grid_x, grid_y] = 0

        # --- Compute Next Generation Based on Selected Mode ---
        if not paused:
            if current_mode == 1:
                neighbors = convolve2d(grid, KERNEL_1, mode='same', boundary='wrap')
                grid = ((neighbors == 3) | ((grid == 1) & (neighbors == 2))).astype(np.uint8)
            
            elif current_mode == 2:
                neighbors = convolve2d(grid, KERNEL_2, mode='same', boundary='wrap')
                grid = ((neighbors == 1) | ((grid == 1) & (neighbors == 2))).astype(np.uint8)
            
            elif current_mode == 3:
                neighbors = convolve2d(grid, KERNEL_3, mode='same', boundary='wrap')
                grid = (((neighbors == 5) | (neighbors == 6)) | 
                        ((grid == 1) & ((neighbors >= 4) & (neighbors <= 7)))).astype(np.uint8)
            
            elif current_mode == 4:
                neighbors = convolve2d(grid, KERNEL_4, mode='same', boundary='wrap')
                grid = (((neighbors >= 7) & (neighbors <= 9)) | 
                        ((grid == 1) & ((neighbors >= 5) & (neighbors <= 7)))).astype(np.uint8)

        # --- Render Animation ---
        rgb_array[grid == 0] = BG_COLOR
        rgb_array[grid == 1] = ALIVE_COLOR

        surface = pygame.surfarray.make_surface(rgb_array)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else 30)

    pygame.quit()

if __name__ == "__main__":
    main()
import pygame
import numpy as np
from scipy.signal import convolve2d

# --- 1. Dimensions & Resolution ---
COLS = 300
ROWS = 175
CELL_SIZE = 4
WIDTH_PX = COLS * CELL_SIZE
HEIGHT_PX = ROWS * CELL_SIZE
PROBABILITY_ALIVE = 0.15  
FADE_SPEED = 8.0 

# --- 2. Visuals ---
BG_COLOR = np.array([18, 18, 24], dtype=np.float32)
ALIVE_COLOR = np.array([0, 255, 170], dtype=np.float32)

# --- 3. Spatial Awareness Kernels ---
KERNEL_1 = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]]) 
KERNEL_2 = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]) 
KERNEL_3 = np.array([[1, 2, 1], [2, 0, 2], [1, 2, 1]]) 
KERNEL_4 = np.ones((5, 5), dtype=int)
KERNEL_4[2, 2] = 0 

def init_grid():
    return np.random.choice([0, 1], size=(COLS, ROWS), p=[1-PROBABILITY_ALIVE, PROBABILITY_ALIVE])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    grid = init_grid()  
    display_rgb = np.full((COLS, ROWS, 3), BG_COLOR, dtype=np.float32)

    running = True
    paused = True
    fade_enabled = True
    current_mode = 1
    current_fps = 15  # Default starting speed
    
    def update_caption():
        status = "Running" if not paused else "Paused"
        fade_status = "ON" if fade_enabled else "OFF"
        modes = {
            1: "Standard Conway", 
            2: "Von Neumann Fractals", 
            3: "Weighted Amoebas", 
            4: "5x5 Macro Islands"
        }
        pygame.display.set_caption(f"[{status} at {current_fps} FPS] Mode {current_mode}: {modes[current_mode]} | Fade: {fade_status} | UP/DOWN to change speed")

    update_caption()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grid = init_grid()
                    display_rgb[:, :] = BG_COLOR
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    update_caption()
                elif event.key == pygame.K_f:
                    fade_enabled = not fade_enabled
                    update_caption()
                elif event.key == pygame.K_c:
                    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
                    display_rgb[:, :] = BG_COLOR
                
                # --- Speed Control Logic ---
                elif event.key == pygame.K_UP:
                    current_fps += 5
                    update_caption()
                elif event.key == pygame.K_DOWN:
                    # Prevent FPS from going to 0 or negative, which crashes clock.tick()
                    current_fps = max(1, current_fps - 5)
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
                if mouse_buttons[0]: 
                    grid[grid_x, grid_y] = 1
                elif mouse_buttons[2]: 
                    grid[grid_x, grid_y] = 0
                    display_rgb[grid_x, grid_y] = BG_COLOR 

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

        # --- Visuals Processing ---
        if fade_enabled:
            if not paused:
                display_rgb -= FADE_SPEED
                display_rgb = np.maximum(display_rgb, BG_COLOR)
        else:
            display_rgb[:, :] = BG_COLOR

        display_rgb[grid == 1] = ALIVE_COLOR

        # --- Render Animation ---
        rgb_array = display_rgb.astype(np.uint8)
        surface = pygame.surfarray.make_surface(rgb_array)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        
        # Apply the dynamic framerate variable here
        clock.tick(60 if paused else current_fps)

    pygame.quit()

if __name__ == "__main__":
    main()
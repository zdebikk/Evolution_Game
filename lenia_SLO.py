import pygame
import numpy as np
from scipy.signal import convolve2d

import ctypes
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass


# --- 1. Dimensions & Resolution ---
COLS = 300
ROWS = 175
CELL_SIZE = 8
WIDTH_PX = COLS * CELL_SIZE
HEIGHT_PX = ROWS * CELL_SIZE

# --- 2. Visuals ---
BG_COLOR = np.array([18, 18, 24], dtype=np.float32)
ALIVE_COLOR = np.array([0, 255, 170], dtype=np.float32)

# --- 3. Continuous Kernel (Smooth Ring) ---
R = 12
Y, X = np.ogrid[-R:R+1, -R:R+1]
dist = np.sqrt(X**2 + Y**2)
KERNEL = np.exp(-(dist - R/2)**2 / (2 * (R/4)**2)).astype(np.float32)
KERNEL /= np.sum(KERNEL) 

def growth_function(U, mu, sigma):
    """Gaussian activation curve using dynamic parameters."""
    return 2.0 * np.exp(-((U - mu)**2) / (2 * sigma**2)) - 1.0

def init_grid():
    """Spawns a concentrated blob of noise in the center to allow outward growth."""
    grid = np.zeros((COLS, ROWS), dtype=np.float32)
    cx, cy = COLS // 2, ROWS // 2
    size = 20  # 40x40 box
    grid[cx-size:cx+size, cy-size:cy+size] = np.random.rand(size*2, size*2)
    return grid

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    grid = init_grid()  

    running = True
    paused = True
    current_fps = 30
    
    # Starting parameters
    mu = 0.135
    sigma = 0.015

    def update_caption():
        status = "Running" if not paused else "Paused"
        pygame.display.set_caption(
            f"[{status}] mu: {mu:.3f} (Q/A) | sigma: {sigma:.3f} (W/S) | FPS: {current_fps} (UP/DOWN)"
        )

    update_caption()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grid = init_grid()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    update_caption()
                elif event.key == pygame.K_c:
                    grid.fill(0.0)
                
                # --- Parameter Tuning Logic ---
                elif event.key == pygame.K_q:
                    mu = round(mu + 0.005, 3)
                    update_caption()
                elif event.key == pygame.K_a:
                    mu = round(max(0.0, mu - 0.005), 3)
                    update_caption()
                elif event.key == pygame.K_w:
                    sigma = round(sigma + 0.001, 3)
                    update_caption()
                elif event.key == pygame.K_s:
                    sigma = round(max(0.001, sigma - 0.001), 3)
                    update_caption()
                
                # --- Speed Control ---
                elif event.key == pygame.K_UP:
                    current_fps += 5
                    update_caption()
                elif event.key == pygame.K_DOWN:
                    current_fps = max(1, current_fps - 5)
                    update_caption()

        # --- Mouse Drawing Logic ---
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] or mouse_buttons[2]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = mouse_x // CELL_SIZE
            grid_y = mouse_y // CELL_SIZE
            
            if 0 < grid_x < COLS-1 and 0 < grid_y < ROWS-1:
                if mouse_buttons[0]: 
                    grid[grid_x-1:grid_x+2, grid_y-1:grid_y+2] = 1.0
                elif mouse_buttons[2]: 
                    grid[grid_x-1:grid_x+2, grid_y-1:grid_y+2] = 0.0

        # --- Compute Continuous Generation ---
        # --- Compute Continuous Generation ---
        if not paused:
            dt = 0.1  # Fractional time step smooths the transitions
            U = convolve2d(grid, KERNEL, mode='same', boundary='wrap')
            growth = growth_function(U, mu, sigma)
            
            # Apply growth smoothly and clamp
            grid = np.clip(grid + growth * dt, 0.0, 1.0)
            
            # Drift threshold clamping (\varepsilon = 0.01)
            grid[grid < 0.01] = 0.0

        # --- Render Continuous Color ---
        display_rgb = BG_COLOR + (ALIVE_COLOR - BG_COLOR) * grid[:, :, np.newaxis]
        rgb_array = display_rgb.astype(np.uint8)
        
        surface = pygame.surfarray.make_surface(rgb_array)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        
        clock.tick(60 if paused else current_fps)

    pygame.quit()

if __name__ == "__main__":
    main()
import sys
import pygame
import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt

# --- 1. Dimensions & Resolution ---
COLS = 300
ROWS = 175
CELL_SIZE = 4
WIDTH_PX = COLS * CELL_SIZE
HEIGHT_PX = ROWS * CELL_SIZE

# --- 2. Species Visual States (RGB Arrays) ---
COLOR_EMPTY = np.array([18, 18, 24], dtype=np.float32)
COLOR_PREY = np.array([0, 255, 170], dtype=np.float32)
COLOR_PRED = np.array([255, 85, 85], dtype=np.float32)

KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])

def main():
    pygame.init()
    
    # Handle fullscreen argument passed from main.py hub
    is_fullscreen = "--fullscreen" in sys.argv
    if is_fullscreen:
        screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
        
    clock = pygame.time.Clock()

    grid = np.random.choice([0, 1, 2], size=(COLS, ROWS), p=[0.90, 0.08, 0.02]).astype(np.uint8)
    
    # --- Fading Buffer Initialization ---
    trail_buffer = np.zeros((COLS, ROWS, 3), dtype=np.float32)
    trail_buffer[:, :] = COLOR_EMPTY
    fading_enabled = True
    fade_speed = 0.88  # Closer to 1.0 = smoother, longer-lasting trails

    # Population history tracker for plotting
    history = {'Prey': [], 'Pred': []}
    
    r_grow = 0.04    
    p_eat = 0.12     
    d_die = 0.08     
    varepsilon = 0.001  

    running = True
    paused = True
    current_fps = 30

    def update_caption():
        status = "Running" if not paused else "Paused"
        fade_status = "ON" if fading_enabled else "OFF"
        pygame.display.set_caption(
            f"Lotka-Volterra [{status}] | Fade: {fade_status} (F) | Grow: {r_grow:.3f} | Eat: {p_eat:.3f} | Die: {d_die:.3f} | 'P' to Plot"
        )

    update_caption()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    update_caption()
                elif event.key == pygame.K_r:
                    grid = np.random.choice([0, 1, 2], size=(COLS, ROWS), p=[0.90, 0.08, 0.02]).astype(np.uint8)
                    trail_buffer[:, :] = COLOR_EMPTY
                    history = {'Prey': [], 'Pred': []}
                
                # --- Toggle Fading via 'F' ---
                elif event.key == pygame.K_f:
                    fading_enabled = not fading_enabled
                    update_caption()

                # --- Fullscreen Toggle via 'X' ---
                elif event.key == pygame.K_x:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))

                # --- Plotting Logic ---
                elif event.key == pygame.K_p:
                    if len(history['Prey']) > 0:
                        plt.figure(figsize=(10, 6))
                        plt.plot(history['Prey'], label='Prey', color='#00ffaa', linewidth=2)
                        plt.plot(history['Pred'], label='Predator', color='#ff5555', linewidth=2)
                        plt.title("Spatial Lotka-Volterra Population Dynamics")
                        plt.xlabel("Time (Generations)")
                        plt.ylabel("Population Count")
                        plt.legend()
                        plt.grid(True, linestyle='--', alpha=0.6)
                        plt.show()

                # --- Parameter Tuning Logic ---
                elif event.key == pygame.K_q:
                    r_grow = min(1.0, r_grow + 0.01); update_caption()
                elif event.key == pygame.K_a:
                    r_grow = max(0.0, r_grow - 0.01); update_caption()
                elif event.key == pygame.K_w:
                    p_eat = min(1.0, p_eat + 0.01); update_caption()
                elif event.key == pygame.K_s:
                    p_eat = max(0.0, p_eat - 0.01); update_caption()
                elif event.key == pygame.K_e:
                    d_die = min(1.0, d_die + 0.01); update_caption()
                elif event.key == pygame.K_d:
                    d_die = max(0.0, d_die - 0.01); update_caption()

        mouse_buttons = pygame.mouse.get_pressed()
        if any(mouse_buttons):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            gx, gy = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            if 0 < gx < COLS-1 and 0 < gy < ROWS-1:
                if mouse_buttons[0]:   
                    grid[gx-2:gx+3, gy-2:gy+3] = 2
                elif mouse_buttons[2]: 
                    grid[gx-2:gx+3, gy-2:gy+3] = 1

        if not paused:
            prey_mask = (grid == 1).astype(np.uint8)
            pred_mask = (grid == 2).astype(np.uint8)
            
            prey_neighbors = convolve2d(prey_mask, KERNEL, mode='same', boundary='wrap')
            pred_neighbors = convolve2d(pred_mask, KERNEL, mode='same', boundary='wrap')
            
            rand_grow = np.random.rand(COLS, ROWS)
            rand_eat = np.random.rand(COLS, ROWS)
            rand_die = np.random.rand(COLS, ROWS)
            
            growth_chance = (prey_neighbors * r_grow) + varepsilon
            new_prey = (grid == 0) & (rand_grow < growth_chance)
            
            eat_chance = pred_neighbors * p_eat
            new_preds = (grid == 1) & (rand_eat < eat_chance)
            
            dead_preds = (grid == 2) & (rand_die < d_die)
            
            grid[new_prey] = 1
            grid[new_preds] = 2
            grid[dead_preds] = 0

            history['Prey'].append(np.count_nonzero(grid == 1))
            history['Pred'].append(np.count_nonzero(grid == 2))

        # --- Smooth Fading Buffer Blend Logic ---
        if fading_enabled:
            # Slowly decay older frames into the background color
            trail_buffer = trail_buffer * fade_speed + COLOR_EMPTY * (1.0 - fade_speed)
        else:
            # Hard reset buffer if fading is toggled off
            trail_buffer[:, :] = COLOR_EMPTY
        
        # Overwrite current living cells with solid colors
        trail_buffer[grid == 1] = COLOR_PREY
        trail_buffer[grid == 2] = COLOR_PRED

        display_rgb = np.clip(trail_buffer, 0, 255).astype(np.uint8)

        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else current_fps)

    pygame.quit()
    sys.exit(11 if is_fullscreen else 10)

if __name__ == "__main__":
    main()
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

# --- 2. Species Visual States ---
COLOR_EMPTY = np.array([18, 18, 24], dtype=np.uint8)
COLOR_PREY = np.array([26, 143, 227], dtype=np.uint8)
COLOR_PREYDARK = np.array([5, 21, 107], dtype=np.uint8)
COLOR_PRED = np.array([255, 195, 0], dtype=np.uint8)

KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    grid = np.random.choice([0, 1, 2, 3], size=(COLS, ROWS), p=[0.90, 0.04, 0.02, 0.04]).astype(np.uint8)
    
    # Population history tracker for plotting
    history = {'Prey': [], 'Pred': [], 'PreyDark': []}
    
    r_grow = 0.04    
    p_eat = 0.12     
    d_die = 0.08     
    varepsilon = 0.001  

    running = True
    paused = True
    current_fps = 30
    frame_count = 0

    # --- Precompute coordinate grid for the background wave ---
    xs = np.arange(COLS)
    ys = np.arange(ROWS)
    X, Y = np.meshgrid(xs, ys, indexing='ij')

    def update_caption():
        status = "Running" if not paused else "Paused"
        pygame.display.set_caption(
            f"My Fish [{status}] at {current_fps} FPS | Grow: {r_grow:.3f} | Eat: {p_eat:.3f} | Die: {d_die:.3f} | Epsilon: {varepsilon:.3f} | 'P' to Plot"
        )

    update_caption()

    while running:
        for event in pygame.event.get():
            # ... (keep all your existing event handling logic here) ...
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    update_caption()
                elif event.key == pygame.K_r:
                    grid = np.random.choice([0, 1, 2, 3], size=(COLS, ROWS), p=[0.90, 0.04, 0.02, 0.04]).astype(np.uint8)
                    history = {'Prey': [], 'Pred': [], 'PreyDark': []}
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
                elif event.key == pygame.K_p:
                    if len(history['Prey']) > 0:
                        plt.figure(figsize=(10, 6))
                        plt.plot(history['Prey'], label='Prey', color='#1A8FE3', linewidth=2)
                        plt.plot(history['Pred'], label='Predator', color='#FFC300', linewidth=2)
                        plt.plot(history['PreyDark'], label='Prey (Dark)', color='#0055ff', linewidth=2)
                        plt.title("Spatial Lotka-Volterra Population Dynamics")
                        plt.xlabel("Time (Generations)")
                        plt.ylabel("Population Count")
                        plt.legend()
                        plt.grid(True, linestyle='--', alpha=0.6)
                        plt.show()
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
                elif event.key == pygame.K_t:
                    varepsilon = min(1.0, varepsilon + 0.001); update_caption()
                elif event.key == pygame.K_g:
                    varepsilon = max(0.0, varepsilon - 0.01); update_caption()
                elif event.key == pygame.K_UP:
                    current_fps += 5; update_caption()
                elif event.key == pygame.K_DOWN:
                    current_fps = max(1, current_fps - 5); update_caption()

        mouse_buttons = pygame.mouse.get_pressed()
        if any(mouse_buttons):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            gx, gy = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            if 0 < gx < COLS-1 and 0 < gy < ROWS-1:
                if mouse_buttons[0]:   
                    grid[gx-2:gx+3, gy-2:gy+3] = 2
                elif mouse_buttons[2]: 
                    grid[gx-2:gx+3, gy-2:gy+3] = 1

        #wave = (0.5 * (np.sin(2*np.pi/COLS* X * 2 +frame_count * 0.02 )) + 0.5)
        #wave = (0.25 * (np.sin(2*np.pi/COLS* X * 2 +frame_count * 0.02 )) + 0.25 * (np.sin(2*np.pi/ROWS* Y * 2 +frame_count * 0.02 )) + 0.5)
        wave = (0.25 * (np.sin(2*np.pi/COLS* X * 3 )) + 0.25 * (np.sin(2*np.pi/ROWS* Y * 2 )))*np.sin(frame_count * 0.02) + 0.5
        if not paused:
            frame_count += 1

            
            prey_mask = (grid == 1).astype(np.uint8)
            preyd_mask = (grid == 3).astype(np.uint8)
            pred_mask = (grid == 2).astype(np.uint8)
            
            prey_neighbors = convolve2d(prey_mask, KERNEL, mode='same', boundary='wrap')
            preyd_neighbors = convolve2d(preyd_mask, KERNEL, mode='same', boundary='wrap')
            pred_neighbors = convolve2d(pred_mask, KERNEL, mode='same', boundary='wrap')
            
            rand_grow = np.random.rand(COLS, ROWS)
            rand_growd = np.random.rand(COLS, ROWS)
            rand_eat = np.random.rand(COLS, ROWS)
            rand_die = np.random.rand(COLS, ROWS)
            
            growth_chance = ((prey_neighbors * r_grow) + varepsilon)
            new_prey = (grid == 0) & (rand_grow < growth_chance/2)

            growth_chanced = ((preyd_neighbors * r_grow) + varepsilon)
            new_preyd = (grid == 0) & (rand_growd < growth_chanced/2)

            eat_chance = (pred_neighbors * p_eat)*wave
            eat_chanced = (pred_neighbors * p_eat)*(1-wave)
            eats_prey = (grid == 1) & (rand_eat < eat_chance)
            eats_preydark = (grid == 3) & (rand_eat < eat_chanced)

            new_preds = eats_prey | eats_preydark
            
            dead_preds = (grid == 2) & (rand_die < d_die)
            
            grid[new_prey] = 1
            grid[new_preyd] = 3
            grid[new_preds] = 2
            grid[dead_preds] = 0

            history['Prey'].append(np.count_nonzero(grid == 1))
            history['Pred'].append(np.count_nonzero(grid == 2))
            history['PreyDark'].append(np.count_nonzero(grid == 3))

        # --- 3. Dynamic Sinusoidal Wave Background Rendering ---
        # Creates a wave marching across the screen mapped from 0 (black) to 255 (white)
        
        bg_intensity = ((wave /20+1/40)*255).astype(np.uint8)
        
        # Build the RGB array using the wave for empty cells (grid == 0)
        display_rgb = np.stack([bg_intensity*1.8, bg_intensity*1.8, bg_intensity*2.4], axis=-1)
        
        # Overlay species colors
        display_rgb[grid == 1] = COLOR_PREY
        display_rgb[grid == 2] = COLOR_PRED
        display_rgb[grid == 3] = COLOR_PREYDARK
        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else current_fps)

    pygame.quit()


if __name__ == "__main__":
    main()
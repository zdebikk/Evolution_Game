import pygame
import numpy as np
from scipy.signal import convolve2d

# --- 1. Dimensions & Resolution ---
COLS = 300
ROWS = 175
CELL_SIZE = 4
WIDTH_PX = COLS * CELL_SIZE
HEIGHT_PX = ROWS * CELL_SIZE

# --- 2. Species Visual States ---
# 0 = Empty (Dark Slate), 1 = Prey (Teal), 2 = Predator (Red)
COLOR_EMPTY = np.array([18, 18, 24], dtype=np.uint8)
COLOR_PREY = np.array([0, 255, 170], dtype=np.uint8)
COLOR_PRED = np.array([255, 85, 85], dtype=np.uint8)

KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    # Initialize grid: 90% Empty, 8% Prey, 2% Predator
    grid = np.random.choice([0, 1, 2], size=(COLS, ROWS), p=[0.90, 0.08, 0.02]).astype(np.uint8)
    
    # Lotka-Volterra Spatial Parameters
    r_grow = 0.04    # Prey reproduction per adjacent prey
    p_eat = 0.12     # Predation probability per adjacent predator
    d_die = 0.08     # Predator death probability per frame
    varepsilon = 0.001  # Spontaneous prey migration (noise)

    running = True
    paused = True
    current_fps = 30

    def update_caption():
        status = "Running" if not paused else "Paused"
        pygame.display.set_caption(
            f"Lotka-Volterra [{status}] | Grow: {r_grow:.3f} (Q/A) | Eat: {p_eat:.3f} (W/S) | Die: {d_die:.3f} (E/D)"
        )

    update_caption()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    update_caption()
                elif event.key == pygame.K_r:
                    grid = np.random.choice([0, 1, 2], size=(COLS, ROWS), p=[0.90, 0.08, 0.02]).astype(np.uint8)
                
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

        # --- Mouse Interaction ---
        mouse_buttons = pygame.mouse.get_pressed()
        if any(mouse_buttons):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            gx, gy = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            if 0 < gx < COLS-1 and 0 < gy < ROWS-1:
                if mouse_buttons[0]:   # Left Click: Drop Predators
                    grid[gx-2:gx+3, gy-2:gy+3] = 2
                elif mouse_buttons[2]: # Right Click: Drop Prey
                    grid[gx-2:gx+3, gy-2:gy+3] = 1

        # --- Compute Stochastic Transitions ---
        if not paused:
            prey_mask = (grid == 1).astype(np.uint8)
            pred_mask = (grid == 2).astype(np.uint8)
            
            prey_neighbors = convolve2d(prey_mask, KERNEL, mode='same', boundary='wrap')
            pred_neighbors = convolve2d(pred_mask, KERNEL, mode='same', boundary='wrap')
            
            rand_grow = np.random.rand(COLS, ROWS)
            rand_eat = np.random.rand(COLS, ROWS)
            rand_die = np.random.rand(COLS, ROWS)
            
            # Rule 1: Empty -> Prey
            growth_chance = (prey_neighbors * r_grow) + varepsilon
            new_prey = (grid == 0) & (rand_grow < growth_chance)
            
            # Rule 2: Prey -> Predator
            eat_chance = pred_neighbors * p_eat
            new_preds = (grid == 1) & (rand_eat < eat_chance)
            
            # Rule 3: Predator -> Empty
            dead_preds = (grid == 2) & (rand_die < d_die)
            
            # Apply state changes
            grid[new_prey] = 1
            grid[new_preds] = 2
            grid[dead_preds] = 0

        # --- Render Visuals ---
        display_rgb = np.empty((COLS, ROWS, 3), dtype=np.uint8)
        
        display_rgb[grid == 0] = COLOR_EMPTY
        display_rgb[grid == 1] = COLOR_PREY
        display_rgb[grid == 2] = COLOR_PRED

        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else current_fps)

    pygame.quit()

if __name__ == "__main__":
    main()
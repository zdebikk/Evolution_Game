import pygame
import numpy as np
from scipy.ndimage import convolve, maximum_filter
import matplotlib.pyplot as plt 

import ctypes
try:
    # Forces Windows to respect the true pixel dimensions
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass # Skips this if you ever run it on Mac/Linux

# --- 1. Dimensions & Resolution ---
COLS = 300
ROWS = 175
CELL_SIZE = 8
WIDTH_PX = COLS * CELL_SIZE
HEIGHT_PX = ROWS * CELL_SIZE

# --- 2. Spatial PD Visual States ---
# Color code from Nowak & Sigmund (2004) Fig 3:
COLOR_D     = np.array([193, 18, 31], dtype=np.uint8)   # Red: sustained D
COLOR_C     = np.array([102, 155, 188], dtype=np.uint8)   # Blue: sustained C
COLOR_NEW_C = np.array([96, 108, 56], dtype=np.uint8)   # Green: new C (was D)
COLOR_NEW_D = np.array([205, 135, 66], dtype=np.uint8)  # Yellow: new D (was C)

# 3x3 Kernel (8 neighbors for playing the game)
KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    # 1 = Cooperator (C), 0 = Defector (D)
    grid = np.ones((COLS, ROWS), dtype=np.uint8)
    # Start with the symmetric initial condition (one D in the center)
    grid[COLS//2, ROWS//2] = 0
    
    prev_grid = grid.copy()
    history = {'C': [], 'D': []}
    
    # Payoff Parameters (Default to Fig 3 values)
    T = 1.40   # Temptation to defect (Q/A)
    R = 1.00   # Reward for mutual cooperation (W/S)
    P = 0.00   # Penalty for mutual defection (E/D)
    S = -0.10  # Sucker's payoff (T/G)

    running = True
    paused = True
    current_fps = 30

    def update_caption():
        status = "Run" if not paused else "Psd"
        pygame.display.set_caption(
            f"Spatial PD [{status}] FPS:{current_fps} | T (q/a):{T:.2f} | R (w/s):{R:.2f} | P (e/d):{P:.2f} | S (t/g):{S:.2f}"
        )

    update_caption()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused; update_caption()
                
                # --- Grid Controls ---
                elif event.key == pygame.K_c:
                    # Clear to a sea of Cooperators with one symmetric Defector in the middle
                    grid = np.ones((COLS, ROWS), dtype=np.uint8)
                    grid[COLS//2, ROWS//2] = 0
                    prev_grid = grid.copy()
                    history = {'C': [], 'D': []}
                elif event.key == pygame.K_r:
                    # Generate random initial conditions
                    grid = np.random.choice([0, 1], size=(COLS, ROWS), p=[0.5, 0.5]).astype(np.uint8)
                    prev_grid = grid.copy()
                    history = {'C': [], 'D': []}
                elif event.key == pygame.K_ESCAPE:
                    running = False
                
                # --- Parameter Tuning Logic ---
                elif event.key == pygame.K_q: T += 0.05; update_caption()
                elif event.key == pygame.K_a: T -= 0.05; update_caption()
                elif event.key == pygame.K_w: R += 0.05; update_caption()
                elif event.key == pygame.K_s: R -= 0.05; update_caption()
                elif event.key == pygame.K_e: P += 0.05; update_caption()
                elif event.key == pygame.K_d: P -= 0.05; update_caption()
                elif event.key == pygame.K_t: S += 0.05; update_caption()
                elif event.key == pygame.K_g: S -= 0.05; update_caption()
                
                # --- FPS Controls ---
                elif event.key == pygame.K_UP: current_fps += 5; update_caption()
                elif event.key == pygame.K_DOWN: current_fps = max(1, current_fps - 5); update_caption()
                
                # --- Plotting ---
                elif event.key == pygame.K_p:
                    if len(history['C']) > 0:
                        plt.figure(figsize=(10, 6), facecolor='#191102')
                        plt.gcf().canvas.mpl_connect(
                            'key_press_event',
                            lambda event: plt.close() if event.key == 'escape' else None
                        )
                        ax = plt.axes()
                        ax.set_facecolor('#191102')
                        plt.plot(history['C'], label='Cooperators', color='#669bbc', linewidth=2)
                        plt.plot(history['D'], label='Defectors', color='#c1121f', linewidth=2)
                        plt.title("Spatial Prisoner's Dilemma Dynamics", color='white')
                        plt.xlabel("Generations", color='white')
                        plt.ylabel("Population Count", color='white')
                        ax.tick_params(colors='white')
                        for spine in ax.spines.values(): spine.set_color('white')
                        plt.legend(facecolor='#191102', edgecolor='white', labelcolor='white')
                        plt.grid(True, linestyle='--', alpha=0.3, color='gray')
                        plt.show()

        # --- Mouse Interaction ---
        mouse_buttons = pygame.mouse.get_pressed()
        if any(mouse_buttons):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            gx, gy = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            if 0 < gx < COLS-1 and 0 < gy < ROWS-1:
                if mouse_buttons[0]:   # L-Click: Draw Defectors (0)
                    grid[gx-2:gx+3, gy-2:gy+3] = 0
                elif mouse_buttons[2]: # R-Click: Draw Cooperators (1)
                    grid[gx-2:gx+3, gy-2:gy+3] = 1

        # --- Compute Stochastic PD Transitions ---
        if not paused:
            prev_grid = grid.copy()
            
            # Maski zostawiamy jako boolean
            mask_c = (grid == 1)
            mask_d = (grid == 0)
            
            # 1. Count neighbors
            # Rzutujemy na uint8 tylko na czas operacji konwolucji
            neighbors_c = convolve(mask_c.astype(np.uint8), KERNEL, mode='wrap')
            neighbors_d = convolve(mask_d.astype(np.uint8), KERNEL, mode='wrap')
            
            # 2. Calculate Payoffs for every cell
            payoffs = np.zeros((COLS, ROWS), dtype=float)
            payoffs[mask_c] = (neighbors_c[mask_c] * R) + (neighbors_d[mask_c] * S)
            payoffs[mask_d] = (neighbors_c[mask_d] * T) + (neighbors_d[mask_d] * P)
            
            # 3. Neighborhood Imitation 
            # (Find the highest scoring C and highest scoring D in the 3x3 window)
            payoffs_c_only = np.where(mask_c, payoffs, -np.inf)
            payoffs_d_only = np.where(mask_d, payoffs, -np.inf)
            
            max_c_in_hood = maximum_filter(payoffs_c_only, size=3, mode='wrap')
            max_d_in_hood = maximum_filter(payoffs_d_only, size=3, mode='wrap')
            
            # The cell adopts the strategy of whoever scored highest in its neighborhood
            grid[max_c_in_hood > max_d_in_hood] = 1
            grid[max_d_in_hood > max_c_in_hood] = 0
            # (Ties keep their current strategy)

            history['C'].append(np.count_nonzero(grid == 1))
            history['D'].append(np.count_nonzero(grid == 0))

        # --- Render Visuals with 4-Color Transition Mapping ---
        display_rgb = np.empty((COLS, ROWS, 3), dtype=np.uint8)
        
        # Determine transition states based on previous and current generation
        sustained_c = (prev_grid == 1) & (grid == 1)
        sustained_d = (prev_grid == 0) & (grid == 0)
        new_c = (prev_grid == 0) & (grid == 1)
        new_d = (prev_grid == 1) & (grid == 0)
        
        display_rgb[sustained_d] = COLOR_D
        display_rgb[sustained_c] = COLOR_C
        display_rgb[new_c] = COLOR_NEW_C
        display_rgb[new_d] = COLOR_NEW_D

        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else current_fps)

    # Bezpieczne zamknięcie i powrót do _main
    pygame.quit()
    return

if __name__ == "__main__":
    main()
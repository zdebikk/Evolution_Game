import pygame
import numpy as np
from scipy.signal import convolve2d
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

# --- 2. SIR Visual States ---
COLOR_S = np.array([40, 44, 52], dtype=np.uint8)     # 0 = Susceptible
COLOR_I = np.array([255, 85, 85], dtype=np.uint8)    # 1 = Infectious
COLOR_R = np.array([97, 175, 239], dtype=np.uint8)   # 2 = Recovered
COLOR_W = np.array([255, 255, 255], dtype=np.uint8)  # 3 = Wall
COLOR_D = np.array([15, 15, 15], dtype=np.uint8)     # 4 = Dead
COLOR_Q = np.array([229, 192, 123], dtype=np.uint8)  # Active Quarantine

# 3x3 Infection Kernel (8 neighbors)
KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])

# 5x5 Quarantine Awareness Kernel (24 neighbors)
Q_KERNEL = np.ones((5, 5), dtype=int)
Q_KERNEL[2, 2] = 0

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
    q_timers = np.zeros((COLS, ROWS), dtype=int) 
    
    # Epidemiological & Spatial Parameters
    beta = 0.05
    alpha = 0.10
    mu = 0.01
    omega = 0.02
    travel_rate = 20
    
    # Quarantine Parameters (Threshold might need to be higher now since the area is larger)
    q_threshold = 7
    q_duration = 30  

    running = True
    paused = True
    current_fps = 30

    history = {'S': [], 'I': [], 'R': [], 'D': []}

    def update_caption():
        status = "Run" if not paused else "Psd"
        pygame.display.set_caption(
            f"[{status}] FPS:{current_fps} | b:{beta:.2f} m:{mu:.2f} | Trvl:{travel_rate} | Q-Thresh(U/J):{q_threshold} Q-Dur(I/K):{q_duration}"
        )

    update_caption()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused; update_caption()
                elif event.key == pygame.K_c:
                    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
                    q_timers = np.zeros((COLS, ROWS), dtype=int)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                
                # Parameter Tuning
                elif event.key == pygame.K_q: beta = min(1.0, beta + 0.005); update_caption()
                elif event.key == pygame.K_a: beta = max(0.0, beta - 0.005); update_caption()
                elif event.key == pygame.K_w: alpha = min(1.0, alpha + 0.005); update_caption()
                elif event.key == pygame.K_s: alpha = max(0.0, alpha - 0.005); update_caption()
                elif event.key == pygame.K_e: mu = min(1.0, mu + 0.005); update_caption()
                elif event.key == pygame.K_d: mu = max(0.0, mu - 0.005); update_caption()
                elif event.key == pygame.K_t: omega = min(1.0, omega + 0.005); update_caption()
                elif event.key == pygame.K_g: omega = max(0.0, omega - 0.005); update_caption()
                elif event.key == pygame.K_y: travel_rate = min(500, travel_rate + 5); update_caption()
                elif event.key == pygame.K_h: travel_rate = max(0, travel_rate - 5); update_caption()
                
                # FPS & Quarantine Controls
                elif event.key == pygame.K_UP: current_fps += 5; update_caption()
                elif event.key == pygame.K_DOWN: current_fps = max(1, current_fps - 5); update_caption()
                elif event.key == pygame.K_u: q_threshold = min(24, q_threshold + 1); update_caption()
                elif event.key == pygame.K_j: q_threshold = max(1, q_threshold - 1); update_caption()
                elif event.key == pygame.K_i: q_duration += 5; update_caption()
                elif event.key == pygame.K_k: q_duration = max(0, q_duration - 5); update_caption()

                elif event.key == pygame.K_p:
                    if len(history['S']) > 0:
                        plt.figure(figsize=(10, 6))
                        plt.gcf().canvas.mpl_connect(
                                                    'key_press_event',
                                                    lambda event: plt.close() if event.key == 'escape' else None
                                                )
                        plt.plot(history['S'], label='Susceptible', color='#282c34', linewidth=2)
                        plt.plot(history['I'], label='Infectious', color='#ff5555', linewidth=2)
                        plt.plot(history['R'], label='Recovered', color='#61afef', linewidth=2)
                        plt.plot(history['D'], label='Dead', color='#0f0f0f', linewidth=2, linestyle=':')
                        plt.title("Spatial SIRS-D with 5x5 Quarantine Awareness")
                        plt.xlabel("Time (Generations)")
                        plt.ylabel("Number of Individuals")
                        plt.legend()
                        plt.grid(True, linestyle='--', alpha=0.6)
                        plt.show()

                elif event.key == pygame.K_r:
                    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
                    q_timers = np.zeros((COLS, ROWS), dtype=int)
                    history = {'S': [], 'I': [], 'R': [], 'D': []}

        # --- Mouse Interaction ---
        mouse_buttons = pygame.mouse.get_pressed()
        if any(mouse_buttons):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            gx, gy = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            if 0 < gx < COLS-1 and 0 < gy < ROWS-1:
                if mouse_buttons[0]:
                    grid[gx-1:gx+2, gy-1:gy+2] = 1
                elif mouse_buttons[2]:
                    grid[gx-1:gx+2, gy-1:gy+2] = 3
                    q_timers[gx-1:gx+2, gy-1:gy+2] = 0 
                elif mouse_buttons[1]:
                    grid[gx-1:gx+2, gy-1:gy+2] = 0
                    q_timers[gx-1:gx+2, gy-1:gy+2] = 0

        # --- Compute Simulation Frame ---
        if not paused:
            # 1. Update existing quarantine timers
            q_timers[q_timers > 0] -= 1

            # 2. Spatial Mobility (Teleportation)
            flat_grid = grid.flatten()
            flat_q = q_timers.flatten()
            valid_indices = np.where((flat_grid != 3) & (flat_q == 0))[0]
            
            if len(valid_indices) > travel_rate * 2 and travel_rate > 0:
                swap_a = np.random.choice(valid_indices, travel_rate, replace=False)
                swap_b = np.random.choice(valid_indices, travel_rate, replace=False)
                
                temp_grid = flat_grid[swap_a]
                flat_grid[swap_a] = flat_grid[swap_b]
                flat_grid[swap_b] = temp_grid
                grid = flat_grid.reshape((COLS, ROWS))

            # 3. Calculate Exposures separately for Infection vs Quarantine
            active_infectious = ((grid == 1) & (q_timers == 0)).astype(np.uint8)
            
            # Infection utilizes the 3x3 KERNEL
            infection_exposure = convolve2d(active_infectious, KERNEL, mode='same', boundary='wrap')
            # Quarantine scanning utilizes the 5x5 Q_KERNEL
            q_exposure = convolve2d(active_infectious, Q_KERNEL, mode='same', boundary='wrap')
            
            # 4. Trigger New Quarantines (using q_exposure)
            new_quarantines = (q_exposure >= q_threshold) & (grid != 3) & (grid != 4) & (q_timers == 0)
            q_timers[new_quarantines] = q_duration

            # 5. Calculate Disease Transitions (using infection_exposure)
            rand_infect = np.random.rand(COLS, ROWS)
            transmission_chance = infection_exposure * beta
            
            new_infections = (grid == 0) & (q_timers == 0) & (rand_infect < transmission_chance)
            
            rand_die = np.random.rand(COLS, ROWS)
            rand_rec = np.random.rand(COLS, ROWS)
            new_dead = (grid == 1) & (rand_die < mu)
            new_recoveries = (grid == 1) & (rand_rec < alpha) & ~new_dead 
            
            rand_decay = np.random.rand(COLS, ROWS)
            lost_immunity = (grid == 2) & (rand_decay < omega)
            
            grid[new_infections] = 1
            grid[new_dead] = 4
            grid[new_recoveries] = 2
            grid[lost_immunity] = 0
            
            q_timers[grid == 4] = 0

            history['S'].append(np.count_nonzero(grid == 0))
            history['I'].append(np.count_nonzero(grid == 1))
            history['R'].append(np.count_nonzero(grid == 2))
            history['D'].append(np.count_nonzero(grid == 4))

        # --- Render Visuals ---
        display_rgb = np.empty((COLS, ROWS, 3), dtype=np.uint8)
        
        display_rgb[grid == 0] = COLOR_S
        display_rgb[grid == 1] = COLOR_I
        display_rgb[grid == 2] = COLOR_R
        display_rgb[grid == 3] = COLOR_W
        display_rgb[grid == 4] = COLOR_D
        
        display_rgb[q_timers > 0] = COLOR_Q

        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else current_fps)

    pygame.quit()

if __name__ == "__main__":
    main()
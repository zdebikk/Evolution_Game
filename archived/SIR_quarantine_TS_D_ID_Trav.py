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

# --- 2. SIR Visual States ---
# 0 = Susceptible (Gray), 1 = Infectious (Red)
# 2 = Recovered (Blue), 3 = Quarantine Wall (White)
# 4 = Dead (Dark Gray)
COLOR_S = np.array([40, 44, 52], dtype=np.uint8)
COLOR_I = np.array([255, 85, 85], dtype=np.uint8)
COLOR_R = np.array([97, 175, 239], dtype=np.uint8)
COLOR_W = np.array([255, 255, 255], dtype=np.uint8)
COLOR_D = np.array([15, 15, 15], dtype=np.uint8)

KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
    
    beta = 0.05   # Transmission probability
    alpha = 0.10  # Recovery probability
    mu = 0.01     # Death probability (E/D keys)
    omega = 0.02  # Immunity decay probability (T/G keys)
    travel_rate = 50  # Travel probability (Y/H keys)

    running = True
    paused = True
    current_fps = 30

    history = {'S': [], 'I': [], 'R': [], 'D': []}

    def update_caption():
        status = "Running" if not paused else "Paused"
        # R0 now accounts for the fact that dying also removes someone from the infectious pool
        r_0 = (8 * beta) / (alpha + mu + 1e-9) 
        pygame.display.set_caption(
            f"SIRS-D | beta: {beta:.3f} | mu: {mu:.3f} | omega: {omega:.3f} | Travel: {travel_rate}"
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
                elif event.key == pygame.K_c:
                    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                
                # --- Parameter Tuning Logic ---
                elif event.key == pygame.K_q:
                    beta = min(1.0, beta + 0.005); update_caption()
                elif event.key == pygame.K_a:
                    beta = max(0.0, beta - 0.005); update_caption()
                elif event.key == pygame.K_w:
                    alpha = min(1.0, alpha + 0.005); update_caption()
                elif event.key == pygame.K_s:
                    alpha = max(0.0, alpha - 0.005); update_caption()
                elif event.key == pygame.K_e:
                    mu = min(1.0, mu + 0.005); update_caption()
                elif event.key == pygame.K_d:
                    mu = max(0.0, mu - 0.005); update_caption()
                elif event.key == pygame.K_t:
                    omega = min(1.0, omega + 0.005); update_caption()
                elif event.key == pygame.K_g:
                    omega = max(0.0, omega - 0.005); update_caption()
                elif event.key == pygame.K_y:
                    travel_rate = min(500, travel_rate + 5); update_caption()
                elif event.key == pygame.K_h:
                    travel_rate = max(0, travel_rate - 5); update_caption()

                elif event.key == pygame.K_p:
                    if len(history['S']) > 0:
                        plt.figure(figsize=(10, 6))
                        plt.plot(history['S'], label='Susceptible', color='#282c34', linewidth=2)
                        plt.plot(history['I'], label='Infectious', color='#ff5555', linewidth=2)
                        plt.plot(history['R'], label='Recovered', color='#61afef', linewidth=2)
                        plt.plot(history['D'], label='Dead', color='#0f0f0f', linewidth=2, linestyle=':')
                        plt.title("Spatial SIRS-D Epidemic Curve")
                        plt.xlabel("Time (Generations)")
                        plt.ylabel("Number of Individuals")
                        plt.legend()
                        plt.grid(True, linestyle='--', alpha=0.6)
                        plt.show()

                elif event.key == pygame.K_r:
                    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
                    history = {'S': [], 'I': [], 'R': [], 'D': []}

        # --- Mouse Interaction: Walls and Infections ---
        mouse_buttons = pygame.mouse.get_pressed()
        if any(mouse_buttons):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            gx, gy = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            if 0 < gx < COLS-1 and 0 < gy < ROWS-1:
                if mouse_buttons[0]:
                    grid[gx-1:gx+2, gy-1:gy+2] = 1
                elif mouse_buttons[2]:
                    grid[gx-1:gx+2, gy-1:gy+2] = 3
                elif mouse_buttons[1]:
                    grid[gx-1:gx+2, gy-1:gy+2] = 0

        # --- Compute Stochastic SIRS-D Transitions ---
        if not paused:

            #TRAVEL LOGIC: Randomly swap individuals in the grid to simulate movement

            flat_grid = grid.flatten()
            valid_indices = np.where(flat_grid != 3)[0]
            
            # Ensure we have enough empty/populated space to actually swap
            if len(valid_indices) > travel_rate * 2 and travel_rate > 0:
                # Select random pairs of coordinates to swap
                swap_a = np.random.choice(valid_indices, travel_rate, replace=False)
                swap_b = np.random.choice(valid_indices, travel_rate, replace=False)
                
                # Perform the simultaneous swap in the 1D array
                temp = flat_grid[swap_a]
                flat_grid[swap_a] = flat_grid[swap_b]
                flat_grid[swap_b] = temp
                
                # Reshape back to the 2D grid
                grid = flat_grid.reshape((COLS, ROWS))
            

            infectious_grid = (grid == 1).astype(np.uint8)
            exposure = convolve2d(infectious_grid, KERNEL, mode='same', boundary='wrap')
            # ---------------------------------------------------------

            infectious_grid = (grid == 1).astype(np.uint8)
            exposure = convolve2d(infectious_grid, KERNEL, mode='same', boundary='wrap')
            
            rand_infect = np.random.rand(COLS, ROWS)
            transmission_chance = exposure * beta
            
            # S -> I (Infection)
            new_infections = (grid == 0) & (rand_infect < transmission_chance)
            
            # I -> D (Death) and I -> R (Recovery)
            # We use two random matrices, but prioritize death to prevent a cell from doing both
            rand_die = np.random.rand(COLS, ROWS)
            rand_rec = np.random.rand(COLS, ROWS)
            
            new_dead = (grid == 1) & (rand_die < mu)
            new_recoveries = (grid == 1) & (rand_rec < alpha) & ~new_dead 
            
            # R -> S (Immunity Decay)
            rand_decay = np.random.rand(COLS, ROWS)
            lost_immunity = (grid == 2) & (rand_decay < omega)
            
            # Apply all transitions simultaneously
            grid[new_infections] = 1
            grid[new_dead] = 4
            grid[new_recoveries] = 2
            grid[lost_immunity] = 0

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

        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else current_fps)

    pygame.quit()

if __name__ == "__main__":
    main()
import pygame
import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
import csv
from datetime import datetime

# --- 1. Dimensions & Resolution ---
COLS = 300
ROWS = 175
CELL_SIZE = 4
WIDTH_PX = COLS * CELL_SIZE
HEIGHT_PX = ROWS * CELL_SIZE

# --- 2. SIR Visual States ---
# 0 = Susceptible (Gray), 1 = Infectious (Red)
# 2 = Recovered (Blue), 3 = Quarantine Wall (White)
COLOR_S = np.array([40, 44, 52], dtype=np.uint8)
COLOR_I = np.array([255, 85, 85], dtype=np.uint8)
COLOR_R = np.array([97, 175, 239], dtype=np.uint8)
COLOR_W = np.array([255, 255, 255], dtype=np.uint8)

KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
    
    beta = 0.05   
    alpha = 0.10  

    running = True
    paused = True
    current_fps = 30

    history = {'S': [], 'I': [], 'R': []}

    def update_caption():
        status = "Running" if not paused else "Paused"
        r_0 = (8 * beta) / alpha
        pygame.display.set_caption(
            f"SIR Grid [{status}] | beta: {beta:.3f} (Q/A) | alpha: {alpha:.3f} (W/S) | R0: {r_0:.2f} | L-Click: Infect, R-Click: Wall"
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
                    beta = min(1.0, beta + 0.005)
                    update_caption()
                elif event.key == pygame.K_a:
                    beta = max(0.0, beta - 0.005)
                    update_caption()
                elif event.key == pygame.K_w:
                    alpha = min(1.0, alpha + 0.005)
                    update_caption()
                elif event.key == pygame.K_s:
                    alpha = max(0.005, alpha - 0.005)
                    update_caption()
                elif event.key == pygame.K_p:
                    if len(history['S']) > 0:
                        plt.figure(figsize=(10, 6))
                        plt.plot(history['S'], label='Susceptible', color='#282c34', linewidth=2)
                        plt.plot(history['I'], label='Infectious', color='#ff5555', linewidth=2)
                        plt.plot(history['R'], label='Recovered', color='#61afef', linewidth=2)
                        plt.title("Spatial SIR Epidemic Curve")
                        plt.xlabel("Time (Generations)")
                        plt.ylabel("Number of Individuals")
                        plt.legend()
                        plt.grid(True, linestyle='--', alpha=0.6)
                        plt.show()
                # If you want to reset the data when you clear the board:
                elif event.key == pygame.K_r:
                    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
                    history = {'S': [], 'I': [], 'R': []}

        # --- Mouse Interaction: Walls and Infections ---
        mouse_buttons = pygame.mouse.get_pressed()
        if any(mouse_buttons):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            gx, gy = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            if 0 < gx < COLS-1 and 0 < gy < ROWS-1:
                # Left Click (0): Drop Infection (State 1)
                if mouse_buttons[0]:
                    grid[gx-1:gx+2, gy-1:gy+2] = 1
                # Right Click (2): Draw Quarantine Wall (State 3)
                elif mouse_buttons[2]:
                    grid[gx-1:gx+2, gy-1:gy+2] = 3
                # Middle Click (1): Erase back to Susceptible (State 0)
                elif mouse_buttons[1]:
                    grid[gx-1:gx+2, gy-1:gy+2] = 0

        # --- Compute Stochastic SIR Transitions ---
        if not paused:
            infectious_grid = (grid == 1).astype(np.uint8)
            exposure = convolve2d(infectious_grid, KERNEL, mode='same', boundary='wrap')
            
            rand_matrix = np.random.rand(COLS, ROWS)
            transmission_chance = exposure * beta
            
            # The grid == 0 constraint guarantees walls (State 3) cannot be infected
            new_infections = (grid == 0) & (rand_matrix < transmission_chance)
            
            rand_matrix_rec = np.random.rand(COLS, ROWS)
            new_recoveries = (grid == 1) & (rand_matrix_rec < alpha)
            
            grid[new_infections] = 1
            grid[new_recoveries] = 2

            history['S'].append(np.count_nonzero(grid == 0))
            history['I'].append(np.count_nonzero(grid == 1))
            history['R'].append(np.count_nonzero(grid == 2))

        # --- Render Visuals ---
        display_rgb = np.empty((COLS, ROWS, 3), dtype=np.uint8)
        
        display_rgb[grid == 0] = COLOR_S
        display_rgb[grid == 1] = COLOR_I
        display_rgb[grid == 2] = COLOR_R
        display_rgb[grid == 3] = COLOR_W

        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else current_fps)

    pygame.quit()

if __name__ == "__main__":
    main()
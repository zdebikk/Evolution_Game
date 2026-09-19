import pygame
import numpy as np
from scipy.signal import convolve2d

# --- 1. Dimensions & Resolution ---
COLS = 300
ROWS = 175
CELL_SIZE = 4
WIDTH_PX = COLS * CELL_SIZE
HEIGHT_PX = ROWS * CELL_SIZE

# --- 2. SIR Visual States ---
# 0 = Susceptible (Gray), 1 = Infectious (Red), 2 = Recovered (Blue)
COLOR_S = np.array([40, 44, 52], dtype=np.uint8)
COLOR_I = np.array([255, 85, 85], dtype=np.uint8)
COLOR_R = np.array([97, 175, 239], dtype=np.uint8)

# Standard Moore Neighborhood for spatial transmission
KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    # Initialize everyone as Susceptible (0)
    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
    
    # Epidemic Parameters
    beta = 0.05   # Probability of transmission per infectious neighbor per frame
    alpha = 0.10  # Probability of recovery per frame

    running = True
    paused = True
    current_fps = 30

    def update_caption():
        status = "Running" if not paused else "Paused"
        # Calculate theoretical R_0 for a 2D Moore neighborhood
        r_0 = (8 * beta) / alpha
        pygame.display.set_caption(
            f"SIR Grid [{status}] | beta: {beta:.3f} (Q/A) | alpha: {alpha:.3f} (W/S) | R0: {r_0:.2f} | SPACE to play"
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
                    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
                
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
                    alpha = max(0.005, alpha - 0.005) # Prevent division by zero
                    update_caption()

        # --- Mouse Interaction: Introduce "Patient Zero" ---
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Left click drops infectious individuals (1)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            gx, gy = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            if 0 < gx < COLS-1 and 0 < gy < ROWS-1:
                # Drop a 3x3 cluster of infections to start the outbreak
                grid[gx-1:gx+2, gy-1:gy+2] = 1

        # --- Compute Stochastic SIR Transitions ---
        if not paused:
            # 1. Isolate the currently infectious cells as a binary matrix
            infectious_grid = (grid == 1).astype(np.uint8)
            
            # 2. Count infectious neighbors for every cell simultaneously
            exposure = convolve2d(infectious_grid, KERNEL, mode='same', boundary='wrap')
            
            # 3. Generate a random matrix for stochastic evaluation
            rand_matrix = np.random.rand(COLS, ROWS)
            
            # 4. Calculate infections: S -> I
            # A susceptible cell gets infected if a random roll is less than the combined transmission chance
            transmission_chance = exposure * beta
            new_infections = (grid == 0) & (rand_matrix < transmission_chance)
            
            # 5. Calculate recoveries: I -> R
            # Re-roll for recovery to ensure statistical independence
            rand_matrix_rec = np.random.rand(COLS, ROWS)
            new_recoveries = (grid == 1) & (rand_matrix_rec < alpha)
            
            # 6. Apply updates
            grid[new_infections] = 1
            grid[new_recoveries] = 2

        # --- Render Visuals ---
        display_rgb = np.empty((COLS, ROWS, 3), dtype=np.uint8)
        
        # Map the states to their respective colors
        display_rgb[grid == 0] = COLOR_S
        display_rgb[grid == 1] = COLOR_I
        display_rgb[grid == 2] = COLOR_R

        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        
        clock.tick(60 if paused else current_fps)

    pygame.quit()

if __name__ == "__main__":
    main()
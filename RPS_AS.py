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

# --- 2. RPS Visual States (Updated Custom Hex Palette) ---
COLOR_EMPTY = np.array([25, 17, 2], dtype=np.uint8)       # #191102 (Background)
COLOR_ROCK = np.array([243, 182, 31], dtype=np.uint8)     # #F3B61F (Amber / Gold)
COLOR_PAPER = np.array([162, 159, 21], dtype=np.uint8)    # #A29F15 (Olive / Moss)
COLOR_SCISSORS = np.array([81, 13, 10], dtype=np.uint8)   # #510D0A (Deep Wine / Blood Red)

KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    # Random uniform distribution of all 4 states initially
    grid = np.random.choice([0, 1, 2, 3], size=(COLS, ROWS), p=[0.70, 0.10, 0.10, 0.10]).astype(np.uint8)
    
    # Trackers for plotting
    history = {'Rock': [], 'Paper': [], 'Scissors': []}
    
    # Parameters
    p_grow = 0.05       # (Q/A) Rate at which a species expands into empty space
    p_beat = 0.15       # (W/S) Rate at which a predator takes over its prey's cell
    p_die = 0.02        # (E/D) Rate at which cells spontaneously die
    varepsilon = 0.001  # (T/G) Spontaneous generation into empty cells
    p_beat_r = 0.22  # Rock invades Scissors faster (advantaged offensively)
    p_beat_p = 0.15  # Paper invades Rock at baseline
    p_beat_s = 0.15  # Scissors invades Paper at baseline

    running = True
    paused = True
    current_fps = 30

    def update_caption():
        status = "Run" if not paused else "Psd"
        pygame.display.set_caption(
            
            f"RPS [{status}] at {current_fps} FPS | Grow(Q/A): {p_grow:.2f} | Eat(W/S): {p_beat:.2f} | Die(E/D): {p_die:.2f} | Epsilon(T/G): {varepsilon:.3f} | p_beat_r(Y/H): {p_beat_r:.2f} | r_beat_s(U/J): {r_beat_s:.2f} | s_beat_p(I/K): {s_beat_p:.2f} | 'P' to Plot"
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
                elif event.key == pygame.K_r:
                    grid = np.random.choice([0, 1, 2, 3], size=(COLS, ROWS), p=[0.7, 0.1, 0.1, 0.1]).astype(np.uint8)
                    history = {'Rock': [], 'Paper': [], 'Scissors': []}
                elif event.key == pygame.K_ESCAPE:
                    running = False
                
                # --- Parameter Tuning Logic ---
                elif event.key == pygame.K_q: p_grow = min(1.0, p_grow + 0.01); update_caption()
                elif event.key == pygame.K_a: p_grow = max(0.0, p_grow - 0.01); update_caption()
                elif event.key == pygame.K_e: p_die = min(1.0, p_die + 0.01); update_caption()
                elif event.key == pygame.K_d: p_die = max(0.0, p_die - 0.01); update_caption()
                elif event.key == pygame.K_t: varepsilon = min(0.1, varepsilon + 0.001); update_caption()
                elif event.key == pygame.K_g: varepsilon = max(0.0, varepsilon - 0.001); update_caption()

                elif event.key == pygame.K_y: p_beat_r = min(1.0, p_beat_r + 0.01); update_caption()
                elif event.key == pygame.K_h: p_beat_r = max(0.0, p_beat_r - 0.01); update_caption()
                elif event.key == pygame.K_u: r_beat_s = min(1.0, r_beat_s + 0.01); update_caption()
                elif event.key == pygame.K_j: r_beat_s = max(0.0, r_beat_s - 0.01); update_caption()
                elif event.key == pygame.K_i: s_beat_p = min(0.1, s_beat_p + 0.01); update_caption()
                elif event.key == pygame.K_k: s_beat_p = max(0.0, s_beat_p - 0.01); update_caption()





                
                # --- FPS Controls ---
                elif event.key == pygame.K_UP: current_fps += 5; update_caption()
                elif event.key == pygame.K_DOWN: current_fps = max(1, current_fps - 5); update_caption()
                
                # --- Plotting ---
                elif event.key == pygame.K_p:
                    if len(history['Rock']) > 0:
                        plt.figure(figsize=(10, 6), facecolor='#191102')
                        ax = plt.axes()
                        ax.set_facecolor('#191102')
                        plt.plot(history['Rock'], label='Rock', color='#F3B61F', linewidth=2)
                        plt.plot(history['Paper'], label='Paper', color='#A29F15', linewidth=2)
                        plt.plot(history['Scissors'], label='Scissors', color='#E04B45', linewidth=2)
                        plt.title("Spatial Rock-Paper-Scissors Dynamics", color='white')
                        plt.xlabel("Time (Generations)", color='white')
                        plt.ylabel("Population Count", color='white')
                        ax.tick_params(colors='white')
                        for spine in ax.spines.values():
                            spine.set_color('white')
                        plt.legend(facecolor='#191102', edgecolor='white', labelcolor='white')
                        plt.grid(True, linestyle='--', alpha=0.3, color='gray')
                        plt.show()

        # --- Mouse Interaction ---
        mouse_buttons = pygame.mouse.get_pressed()
        if any(mouse_buttons):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            gx, gy = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            if 0 < gx < COLS-1 and 0 < gy < ROWS-1:
                if mouse_buttons[0]:   # L-Click: Spawn Rock
                    grid[gx-2:gx+3, gy-2:gy+3] = 1
                elif mouse_buttons[1]: # M-Click: Spawn Scissors
                    grid[gx-2:gx+3, gy-2:gy+3] = 3
                elif mouse_buttons[2]: # R-Click: Spawn Paper
                    grid[gx-2:gx+3, gy-2:gy+3] = 2

        # --- Compute Stochastic RPS Transitions ---
        if not paused:
            mask_r = (grid == 1).astype(np.uint8)
            mask_p = (grid == 2).astype(np.uint8)
            mask_s = (grid == 3).astype(np.uint8)
            
            neighbors_r = convolve2d(mask_r, KERNEL, mode='same', boundary='wrap')
            neighbors_p = convolve2d(mask_p, KERNEL, mode='same', boundary='wrap')
            neighbors_s = convolve2d(mask_s, KERNEL, mode='same', boundary='wrap')
            
            # 1. Attack Logic
            r_to_p = (grid == 1) & (np.random.rand(COLS, ROWS) < neighbors_p * p_beat_p)
            p_to_s = (grid == 2) & (np.random.rand(COLS, ROWS) < neighbors_s * p_beat_s)
            s_to_r = (grid == 3) & (np.random.rand(COLS, ROWS) < neighbors_r * p_beat_r)
            
            # 2. Growth Logic
            empty = (grid == 0)
            rand_grow_r = np.random.rand(COLS, ROWS)
            rand_grow_p = np.random.rand(COLS, ROWS)
            rand_grow_s = np.random.rand(COLS, ROWS)
            
            empty_to_r = empty & (rand_grow_r < (neighbors_r * p_grow) + varepsilon)
            empty_to_p = empty & (rand_grow_p < (neighbors_p * p_grow) + varepsilon)
            empty_to_s = empty & (rand_grow_s < (neighbors_s * p_grow) + varepsilon)
            
            # 3. Death Logic
            die = (grid != 0) & (np.random.rand(COLS, ROWS) < p_die)
            
            # Apply Updates
            grid[r_to_p] = 2
            grid[p_to_s] = 3
            grid[s_to_r] = 1
            
            grid[empty_to_r] = 1
            grid[empty_to_p] = 2
            grid[empty_to_s] = 3
            
            grid[die] = 0

            # Record history
            history['Rock'].append(np.count_nonzero(grid == 1))
            history['Paper'].append(np.count_nonzero(grid == 2))
            history['Scissors'].append(np.count_nonzero(grid == 3))

        # --- Render Visuals ---
        display_rgb = np.empty((COLS, ROWS, 3), dtype=np.uint8)
        
        display_rgb[grid == 0] = COLOR_EMPTY
        display_rgb[grid == 1] = COLOR_ROCK
        display_rgb[grid == 2] = COLOR_PAPER
        display_rgb[grid == 3] = COLOR_SCISSORS

        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else current_fps)


if __name__ == "__main__":
    main()
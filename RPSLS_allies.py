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

# --- 2. RPSLS Visual States ---
COLOR_EMPTY = np.array([25, 17, 2], dtype=np.uint8)       # Background
COLOR_ROCK = np.array([243, 182, 31], dtype=np.uint8)     # 1: Amber
COLOR_PAPER = np.array([162, 159, 21], dtype=np.uint8)    # 2: Olive
COLOR_SCISSORS = np.array([81, 13, 10], dtype=np.uint8)   # 3: Deep Wine
COLOR_SPOCK = np.array([101, 142, 156], dtype=np.uint8)    # 4: Blue
COLOR_LIZARD = np.array([122, 86, 16], dtype=np.uint8)    # 5: Green

KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    init_probs = [0.70, 0.06, 0.06, 0.06, 0.06, 0.06]
    grid = np.random.choice([0, 1, 2, 3, 4, 5], size=(COLS, ROWS), p=init_probs).astype(np.uint8)
    
    history = {'Rock': [], 'Paper': [], 'Scissors': [], 'Spock': [], 'Lizard': []}
    
    p_grow = 0.05       
    p_beat = 0.15       
    p_die = 0.02        
    varepsilon = 0.001  

    running = True
    paused = True
    current_fps = 30

    def update_caption():
        status = "Run" if not paused else "Psd"
        pygame.display.set_caption(
            f"Alliance RPSLS [{status}] FPS:{current_fps} | Grow:{p_grow:.2f} | Beat:{p_beat:.2f} | Die:{p_die:.2f} | Varepsilon:{varepsilon:.3f}"
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
                    grid = np.random.choice([0, 1, 2, 3, 4, 5], size=(COLS, ROWS), p=init_probs).astype(np.uint8)
                    history = {k: [] for k in history}
                elif event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_q: p_grow = min(1.0, p_grow + 0.01); update_caption()
                elif event.key == pygame.K_a: p_grow = max(0.0, p_grow - 0.01); update_caption()
                elif event.key == pygame.K_w: p_beat = min(1.0, p_beat + 0.01); update_caption()
                elif event.key == pygame.K_s: p_beat = max(0.0, p_beat - 0.01); update_caption()
                elif event.key == pygame.K_e: p_die = min(1.0, p_die + 0.01); update_caption()
                elif event.key == pygame.K_d: p_die = max(0.0, p_die - 0.01); update_caption()
                elif event.key == pygame.K_t: varepsilon = min(0.1, varepsilon + 0.001); update_caption()
                elif event.key == pygame.K_g: varepsilon = max(0.0, varepsilon - 0.001); update_caption()
                
                elif event.key == pygame.K_UP: current_fps += 5; update_caption()
                elif event.key == pygame.K_DOWN: current_fps = max(1, current_fps - 5); update_caption()
                
                elif event.key == pygame.K_p:
                    if len(history['Rock']) > 0:
                        plt.figure(figsize=(10, 6), facecolor='#191102')
                        ax = plt.axes()
                        ax.set_facecolor('#191102')
                        plt.plot(history['Rock'], label='Rock (Team A)', color='#F3B61F', linewidth=1.5)
                        plt.plot(history['Spock'], label='Spock (Team A)', color='#4287f5', linewidth=1.5)
                        plt.plot(history['Paper'], label='Paper (Team B)', color='#A29F15', linewidth=1.5)
                        plt.plot(history['Scissors'], label='Scissors (Team B)', color='#510D0A', linewidth=1.5)
                        plt.plot(history['Lizard'], label='Lizard (Team C)', color='#7A5610', linewidth=1.5)
                        plt.title("Alliance Dynamics (Team A -> Team B -> Team C -> Team A)", color='white')
                        plt.xlabel("Generations", color='white')
                        plt.ylabel("Population", color='white')
                        ax.tick_params(colors='white')
                        for spine in ax.spines.values(): spine.set_color('white')
                        plt.legend(facecolor='#191102', edgecolor='white', labelcolor='white')
                        plt.grid(True, linestyle='--', alpha=0.3, color='gray')
                        plt.show()

        mouse_buttons = pygame.mouse.get_pressed()
        if any(mouse_buttons):
            mouse_x, mouse_y = pygame.mouse.get_pos()
            gx, gy = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
            if 0 < gx < COLS-1 and 0 < gy < ROWS-1:
                grid[gx-3:gx+4, gy-3:gy+4] = np.random.choice([1, 2, 3, 4, 5], size=(7, 7))

        if not paused:
            masks = {i: (grid == i).astype(np.uint8) for i in range(1, 6)}
            neighbors = {i: convolve2d(masks[i], KERNEL, mode='same', boundary='wrap') for i in range(1, 6)}
            
            rand_atk = np.random.rand(COLS, ROWS)
            
            # --- ALLIANCE INVASION LOGIC ---
            
            # Team A (Rock & Spock) attacks Team B (Paper & Scissors)
            p_to_r = (grid == 2) & (rand_atk < neighbors[1] * p_beat)
            s_to_r = (grid == 3) & (rand_atk < neighbors[1] * p_beat)
            p_to_sp = (grid == 2) & (rand_atk < neighbors[4] * p_beat)
            s_to_sp = (grid == 3) & (rand_atk < neighbors[4] * p_beat)
            
            # Team B (Paper & Scissors) attacks Team C (Lizard)
            l_to_p = (grid == 5) & (rand_atk < neighbors[2] * p_beat)
            l_to_s = (grid == 5) & (rand_atk < neighbors[3] * p_beat)
            
            # Team C (Lizard) attacks Team A (Rock & Spock)
            r_to_l = (grid == 1) & (rand_atk < neighbors[5] * p_beat)
            sp_to_l = (grid == 4) & (rand_atk < neighbors[5] * p_beat)

            # Growth Logic
            empty = (grid == 0)
            empty_to = {}
            for i in range(1, 6):
                empty_to[i] = empty & (np.random.rand(COLS, ROWS) < (neighbors[i] * p_grow) + varepsilon)
            
            # Death Logic
            die = (grid != 0) & (np.random.rand(COLS, ROWS) < p_die)
            
            # Apply Invasions
            grid[p_to_r] = 1; grid[s_to_r] = 1
            grid[p_to_sp] = 4; grid[s_to_sp] = 4
            
            grid[l_to_p] = 2; grid[l_to_s] = 3
            
            grid[r_to_l] = 5; grid[sp_to_l] = 5
            
            # Apply Growth & Death
            for i in range(1, 6):
                grid[empty_to[i]] = i
            grid[die] = 0

            # Record Metrics
            history['Rock'].append(np.count_nonzero(grid == 1))
            history['Paper'].append(np.count_nonzero(grid == 2))
            history['Scissors'].append(np.count_nonzero(grid == 3))
            history['Spock'].append(np.count_nonzero(grid == 4))
            history['Lizard'].append(np.count_nonzero(grid == 5))

        # --- Render Visuals ---
        display_rgb = np.empty((COLS, ROWS, 3), dtype=np.uint8)
        
        display_rgb[grid == 0] = COLOR_EMPTY
        display_rgb[grid == 1] = COLOR_ROCK
        display_rgb[grid == 2] = COLOR_PAPER
        display_rgb[grid == 3] = COLOR_SCISSORS
        display_rgb[grid == 4] = COLOR_SPOCK
        display_rgb[grid == 5] = COLOR_LIZARD

        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else current_fps)

    pygame.quit()

if __name__ == "__main__":
    main()
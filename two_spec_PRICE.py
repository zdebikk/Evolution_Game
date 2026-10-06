import pygame
import numpy as np
from scipy.ndimage import convolve
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

# --- 2. Species Visual States ---
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

    grid = np.random.choice([0, 1, 2], size=(COLS, ROWS), p=[0.90, 0.08, 0.02]).astype(np.uint8)
    
    # Population history tracker for plotting
    history = {'Prey': [], 'Pred': [], 'Covariance': [], 'Expectation': []}
    
    r_grow = 0.04    
    p_eat = 0.12     
    d_die = 0.08     
    varepsilon = 0.001  

    running = True
    paused = True
    current_fps = 30

    def update_caption():
        status = "Running" if not paused else "Paused"
        pygame.display.set_caption(
            f"Lotka-Volterra [{status}] at {current_fps} FPS | Grow(Q/A): {r_grow:.3f} | Eat(W/S): {p_eat:.3f} | Die(E/D): {d_die:.3f} | Epsilon(T/G): {varepsilon:.3f} | 'P' to Plot"
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
                    # Reset both grid and history
                    grid = np.random.choice([0, 1, 2], size=(COLS, ROWS), p=[0.90, 0.08, 0.02]).astype(np.uint8)
                    history = {'Prey': [], 'Pred': [], 'Covariance': [], 'Expectation': []}
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    grid = np.zeros((COLS, ROWS), dtype=np.uint8)
                
                # --- Plotting Logic ---
                elif event.key == pygame.K_p:
                    if len(history['Prey']) > 0 and 'Covariance' in history:
                        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
                        fig.canvas.mpl_connect(
                            'key_press_event',
                            lambda event: plt.close() if event.key == 'escape' else None
                        )
                        
                        # Panel 1: Surowa dynamika Lotki-Volterry
                        ax1.plot(history['Prey'], label='Prey', color='#00ffaa', linewidth=2)
                        ax1.plot(history['Pred'], label='Predator', color='#ff5555', linewidth=2)
                        ax1.set_title("Spatial Lotka-Volterra Population Dynamics")
                        ax1.set_ylabel("Population Count")
                        ax1.legend()
                        ax1.grid(True, linestyle='--', alpha=0.6)
                        
                        # Panel 2: Komponenty Równania Price'a
                        ax2.plot(history['Covariance'], label='Covariance (Between-group Selection)', color='#55aaff', linewidth=1.5)
                        ax2.plot(history['Expectation'], label='Expectation (Within-group Transmission)', color='#ffaa00', linewidth=1.5)
                        
                        # Zgodnie z równaniem Price'a: Total = Covariance + Expectation
                        price_total = np.array(history['Covariance']) + np.array(history['Expectation'])
                        ax2.plot(price_total, label='Price Total $\Delta p$', color='white', linestyle='-', linewidth=2)
                        
                        # Nakładka czystej zmiany gęstości ofiar (lewa strona równania)
                        # Omijamy pierwszą iterację, bo liczymy deltę wstecz
                        # Jeśli model matematyczny jest szczelny, linia Total powinna pokrywać się z faktyczną Deltą
                        # (Z dokładnością do błędu aproksymacji na brzegach okien)
                        ax2.set_title("Price Equation Mechanics")
                        ax2.set_xlabel("Time (Generations)")
                        ax2.set_ylabel("Effect Magnitude")
                        ax2.legend()
                        ax2.grid(True, linestyle='--', alpha=0.6)
                        
                        # Ustawienie tła wykresów na ciemne dla czytelności z Pygame
                        for ax in (ax1, ax2):
                            ax.set_facecolor('#121218')
                        fig.patch.set_facecolor('#121218')
                        for text in fig.texts:
                            text.set_color('white')
                        for ax in (ax1, ax2):
                            ax.tick_params(colors='white')
                            ax.xaxis.label.set_color('white')
                            ax.yaxis.label.set_color('white')
                            ax.title.set_color('white')
                            legend = ax.legend(facecolor='#121218', edgecolor='white')
                            for text in legend.get_texts():
                                text.set_color('white')

                        plt.tight_layout()
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
                elif event.key == pygame.K_t:
                    varepsilon = min(1.0, varepsilon + 0.001); update_caption()
                elif event.key == pygame.K_g:
                    varepsilon = max(0.0, varepsilon - 0.01); update_caption()


                # --- Speed Control Logic ---
                elif event.key == pygame.K_UP:
                    current_fps += 5
                    update_caption()
                elif event.key == pygame.K_DOWN:
                    # Prevent FPS from going to 0 or negative, which crashes clock.tick()
                    current_fps = max(1, current_fps - 5)
                    update_caption()

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
            
            prey_neighbors = convolve(prey_mask, KERNEL, mode='wrap')
            pred_neighbors = convolve(pred_mask, KERNEL, mode='wrap')
            
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

            # 1. Stan przed i po aktualizacji (rzutowane na float do obliczeń)
            prey_mask_t = prey_mask.astype(float)
            prey_mask_t1 = (grid == 1).astype(float)
            
            # 2. Podział planszy na wirtualne okna badawcze (subpopulacje 5x5)
            # Reshape grupuje matrycę (300, 175) w bloki, a mean() uśrednia ich zawartość
            window = 5
            p_i = prey_mask_t.reshape(COLS//window, window, ROWS//window, window).mean(axis=(1, 3)).flatten()
            p_prime_i = prey_mask_t1.reshape(COLS//window, window, ROWS//window, window).mean(axis=(1, 3)).flatten()
            
            # 3. Wyliczenie dostosowania (fitness) każdego okna
            # Dodajemy epsilon numeryczny, by uniknąć dzielenia przez zero w martwych polach
            w_i = p_prime_i / (p_i + 1e-8)
            w_avg = np.mean(w_i)
            
            # 4. Aplikacja komponentów Równania Price'a
            if w_avg > 0:
                # Człon kowariancji (dobór międzygrupowy)
                cov_term = np.cov(p_i, w_i)[0, 1] / w_avg
                
                # Człon transmisji / błędu replikacji (dobór wewnątrzgrupowy)
                dp_i = p_prime_i - p_i
                exp_term = np.mean(w_i * dp_i) / w_avg
            else:
                cov_term, exp_term = 0.0, 0.0

            # 5. Zapis wyników
            history['Prey'].append(np.count_nonzero(grid == 1))
            history['Pred'].append(np.count_nonzero(grid == 2))
            history['Covariance'].append(cov_term)
            history['Expectation'].append(exp_term)

        display_rgb = np.empty((COLS, ROWS, 3), dtype=np.uint8)
        
        display_rgb[grid == 0] = COLOR_EMPTY
        display_rgb[grid == 1] = COLOR_PREY
        display_rgb[grid == 2] = COLOR_PRED

        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else current_fps)


if __name__ == "__main__":
    main()
import pygame
import numpy as np
from scipy.ndimage import convolve
from scipy.ndimage import maximum_filter
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

# --- 2. Spatial IPD Visual States ---

COLOR_ALLD = np.array([133, 23, 32], dtype=np.uint8)   # Red: sustained D
COLOR_ALLC = np.array([0, 61, 87], dtype=np.uint8)   # Blue: sustained C
COLOR_TFT = np.array([253, 240, 213], dtype=np.uint8)   # Green: new C (was D)

# 3x3 Kernel (8 neighbors for playing the game)
KERNEL = np.array([[1, 1, 1], 
                   [1, 0, 1], 
                   [1, 1, 1]])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_PX, HEIGHT_PX))
    clock = pygame.time.Clock()

    # 1 = Cooperator (C), 0 = Defector (D), 2 = Tit-for-Tat (TFT)
    grid = np.ones((COLS, ROWS), dtype=np.uint8)
    grid[COLS//2, ROWS//2] = 0
    
    history = {'AllD': [], 'AllC': [], 'TFT': []}
    
    # Payoff Parameters
    T = 1.40   # Temptation to defect (Q/A)
    R = 1.00   # Reward for mutual cooperation (W/S)
    P = 0.40   # Penalty for mutual defection (E/D)
    S = 0.45  # Sucker's payoff (T/G)

    running = True
    paused = True
    current_fps = 30
    m_rounds = 10

    def update_caption():
        status = "Run" if not paused else "Psd"
        pygame.display.set_caption(
            f"Spatial IPD [{status}] FPS:{current_fps} | T:{T:.2f} | R:{R:.2f} | P:{P:.2f} | S:{S:.2f}"
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
                    grid = np.ones((COLS, ROWS), dtype=np.uint8)
                    grid[COLS//2, ROWS//2] = 0
                    history = {'AllD': [], 'AllC': [], 'TFT': []}
                elif event.key == pygame.K_r:
                    grid = np.random.choice([0, 1, 2], size=(COLS, ROWS), p=[0.33, 0.33, 0.34]).astype(np.uint8)
                    history = {'AllD': [], 'AllC': [], 'TFT': []}
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
                    if len(history['AllD']) > 0:
                        plt.figure(figsize=(10, 6), facecolor='#191102')
                        plt.gcf().canvas.mpl_connect(
                            'key_press_event',
                            lambda event: plt.close() if event.key == 'escape' else None
                        )
                        ax = plt.axes()
                        ax.set_facecolor('#191102')
                        
                        plt.plot(history['AllD'], label='AllD (Defectors)', color='#dc1e1e', linewidth=2)
                        plt.plot(history['AllC'], label='AllC (Cooperators)', color='#1e50dc', linewidth=2)
                        plt.plot(history['TFT'], label='TFT (Tit-for-Tat)', color='#2da856', linewidth=2)
                        
                        plt.title("Spatial Iterated Prisoner's Dilemma Dynamics", color='white')
                        plt.xlabel("Generations", color='white')
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
                if mouse_buttons[0]:   # L-Click: Draw Defectors (0)
                    grid[gx-2:gx+3, gy-2:gy+3] = 0
                elif mouse_buttons[2]: # R-Click: Draw Cooperators (1)
                    grid[gx-2:gx+3, gy-2:gy+3] = 1
                elif mouse_buttons[1]: # M-Click: Draw TFT (2)
                    grid[gx-2:gx+3, gy-2:gy+3] = 2

        # --- Compute Stochastic IPD Transitions (AllC, AllD, TFT) ---
        if not paused:
            # Zachowujemy maski jako wartości logiczne (True/False) do późniejszego indeksowania
            mask_alld = (grid == 0)
            mask_allc = (grid == 1)
            mask_tft  = (grid == 2)
            
            # 1. Count neighbors of each strategy type
            # Konwertujemy na uint8 tylko w momencie splotu dla zwiększenia wydajności
            n_alld = convolve(mask_alld.astype(np.uint8), KERNEL, mode='wrap')
            n_allc = convolve(mask_allc.astype(np.uint8), KERNEL, mode='wrap')
            n_tft  = convolve(mask_tft.astype(np.uint8), KERNEL, mode='wrap')
            
            # 2. Calculate Expected Payoffs over m_rounds
            payoffs = np.zeros((COLS, ROWS), dtype=float)
            
            # AllD payoffs
            payoffs[mask_alld] = (n_alld[mask_alld] * (m_rounds * P) + 
                                  n_allc[mask_alld] * (m_rounds * T) + 
                                  n_tft[mask_alld]  * (T + (m_rounds - 1) * P))
            
            # AllC payoffs
            payoffs[mask_allc] = (n_alld[mask_allc] * (m_rounds * S) + 
                                  n_allc[mask_allc] * (m_rounds * R) + 
                                  n_tft[mask_allc]  * (m_rounds * R))
                                  
            # TFT payoffs
            payoffs[mask_tft] =  (n_alld[mask_tft] * (S + (m_rounds - 1) * P) + 
                                  n_allc[mask_tft] * (m_rounds * R) + 
                                  n_tft[mask_tft]  * (m_rounds * R))
            
            # 3. Neighborhood Imitation (Find the highest scoring strategy in the 3x3 window)
            payoffs_alld_only = np.where(mask_alld, payoffs, -np.inf)
            payoffs_allc_only = np.where(mask_allc, payoffs, -np.inf)
            payoffs_tft_only  = np.where(mask_tft, payoffs, -np.inf)
            
            max_alld_hood = maximum_filter(payoffs_alld_only, size=3, mode='wrap')
            max_allc_hood = maximum_filter(payoffs_allc_only, size=3, mode='wrap')
            max_tft_hood  = maximum_filter(payoffs_tft_only, size=3, mode='wrap')
            
            # 4. Apply the winning strategies without np.stack()
            # Startujemy z założenia, że najlepszy jest AllD (0)
            grid = np.zeros((COLS, ROWS), dtype=np.uint8)
            best_payoffs = max_alld_hood
            
            # Sprawdzamy czy AllC (1) daje lepszy wynik
            better_than_alld = max_allc_hood > best_payoffs
            best_payoffs = np.where(better_than_alld, max_allc_hood, best_payoffs)
            grid[better_than_alld] = 1
            
            # Sprawdzamy czy TFT (2) daje jeszcze lepszy wynik
            better_than_best = max_tft_hood > best_payoffs
            grid[better_than_best] = 2
            # Record metrics
            history['AllD'].append(np.count_nonzero(grid == 0))
            history['AllC'].append(np.count_nonzero(grid == 1))
            history['TFT'].append(np.count_nonzero(grid == 2))

        # --- Render Visuals ---
        display_rgb = np.zeros((COLS, ROWS, 3), dtype=np.uint8)
        
        display_rgb[grid == 0] = COLOR_ALLD
        display_rgb[grid == 1] = COLOR_ALLC
        display_rgb[grid == 2] = COLOR_TFT

        surface = pygame.surfarray.make_surface(display_rgb)
        scaled_surface = pygame.transform.scale(surface, (WIDTH_PX, HEIGHT_PX))
        
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60 if paused else current_fps)
        
    # Bezpieczne zamknięcie okna po wyjściu z pętli i powrót do nadrzędnego skryptu
    pygame.quit()
    return

if __name__ == "__main__":
    main()
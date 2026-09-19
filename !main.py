import sys
import subprocess
import pygame

# --- Configuration ---
WIDTH = 800
HEIGHT = 600
BG_COLOR = (18, 18, 24)
TEXT_COLOR = (200, 200, 200)
HIGHLIGHT = (0, 255, 170)
WARNING_COLOR = (255, 85, 85)

# Map menu options to your most advanced script versions based on your directory
SIMULATIONS = {
    pygame.K_1: "conway_kernel_FO_SLO+.py",
    pygame.K_2: "lenia_SLO+.py",
    pygame.K_3: "SIR_quarantine_TS_D_ID_Trav_SLO_AQ+.py",
    pygame.K_4: "two_spec_TS+.py",
    pygame.K_5: "rybki_fale+.py"  
}

INSTRUCTIONS_TEXT = [
    "--- UNIVERSAL CONTROLS ---",
    "SPACE : Pause/Resume",
    "UP/DN : Adjust Simulation Speed (FPS)",
    "R     : Reset Grid to Initial State",
    "C     : Clear Grid completely",
    "",
    "--- [1] DISCRETE CONWAY KERNELS ---",
    "1-4   : Switch Spatial Kernels",
    "F     : Toggle Visual Fade-Out",
    "L/R-Click : Draw / Erase Cells",
    "",
    "--- [2] CONTINUOUS LENIA ---",
    "Q / A : Increase / Decrease target density (mu)",
    "W / S : Increase / Decrease tolerance (sigma)",
    "L/R-Click : Drop / Erase 3x3 Continuous Mass",
    "",
    "--- [3] SPATIAL SIR EPIDEMIC ---",
    "Q / A : Increase / Decrease Infection Rate (beta)",
    "W / S : Increase / Decrease Recovery Rate (alpha)",
    "P     : Generate Matplotlib Epidemic Curve",
    "Clicks: Left=Infect, Right=Quarantine Wall, Mid=Erase",
    "",
    "--- [4/5] LOTKA-VOLTERRA DYNAMICS ---",
    "Q / A : Adjust Prey Growth Rate",
    "W / S : Adjust Predation Rate",
    "E / D : Adjust Predator Death Rate",
    "P     : Generate Matplotlib Population Curve",
    "Clicks: Left=Drop Predators, Right=Drop Prey",
    "",
    "Press ESC or 'I' to return to the Main Menu."
]

def render_multiline(screen, text_list, font, start_x, start_y, color):
    """Utility to render arrays of text to the Pygame surface."""
    y = start_y
    for line in text_list:
        if line.startswith("---"):
            surface = font.render(line, True, HIGHLIGHT)
        else:
            surface = font.render(line, True, color)
        screen.blit(surface, (start_x, y))
        y += font.get_linesize() + 2

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Evolution Game - Central Hub")
    clock = pygame.time.Clock()

    font_large = pygame.font.SysFont("consolas", 32, bold=True)
    font_medium = pygame.font.SysFont("consolas", 20)
    font_small = pygame.font.SysFont("consolas", 16)

    show_instructions = False

    while True:
        screen.fill(BG_COLOR)

        if show_instructions:
            render_multiline(screen, INSTRUCTIONS_TEXT, font_small, 40, 40, TEXT_COLOR)
        else:
            # Main Menu Rendering
            title = font_large.render("GAME of LIFE", True, HIGHLIGHT)
            opt1 = font_medium.render("[1] Conway Custom Kernels", True, TEXT_COLOR)
            opt2 = font_medium.render("[2] Continuous Automaton (Lenia)", True, TEXT_COLOR)
            opt3 = font_medium.render("[3] Spatial SIR Epidemic", True, TEXT_COLOR)
            opt4 = font_medium.render("[4] Lotka-Volterra Predator/Prey", True, TEXT_COLOR)
            opt5 = font_medium.render("[5] My Fish", True, TEXT_COLOR)
            
            info = font_medium.render("Press [I] to view all controls & instructions", True, HIGHLIGHT)
            quit_opt = font_medium.render("[ESC] Quit", True, WARNING_COLOR)

            screen.blit(title, (50, 50))
            screen.blit(opt1, (50, 140))
            screen.blit(opt2, (50, 190))
            screen.blit(opt3, (50, 240))
            screen.blit(opt4, (50, 290))
            screen.blit(opt5, (50, 340))
            screen.blit(info, (50, 420))
            screen.blit(quit_opt, (50, 480))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # If instructions are open, close them. Otherwise, quit.
                    if show_instructions:
                        show_instructions = False
                    else:
                        pygame.quit()
                        sys.exit()
                        
                elif event.key == pygame.K_i:
                    show_instructions = not show_instructions
                    
                # Launch selected script if on the main menu
                elif not show_instructions and event.key in SIMULATIONS:
                    target_script = SIMULATIONS[event.key]
                    
                    # Update caption to show it is running
                    pygame.display.set_caption(f"Running: {target_script}...")
                    
                    # Launch the script using the current virtual environment's Python interpreter
                    subprocess.Popen([sys.executable, target_script]).wait()
                    
                    # Restore caption when the child script is closed
                    pygame.display.set_caption("Evolution Game - Central Hub")

        clock.tick(15)

if __name__ == "__main__":
    main()
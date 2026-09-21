import ctypes
import os
import sys
import subprocess
import pygame

os.environ['SDL_VIDEO_CENTERED'] = '1'

import conway_kernel_FO_SLO
import lenia_SLO
import SIR_quarantine_TS_D_ID_Trav_SLO_AQ
import two_spec_TS
import rybki_fale
import RPS_AS
import prison
import prison_TFT

# --- Configuration ---
WIDTH = 2400
HEIGHT = 175*8
BG_COLOR = (18, 18, 24)
TEXT_COLOR = (200, 200, 200)
HIGHLIGHT = (0, 255, 170)
WARNING_COLOR = (255, 85, 85)

# Map menu options to your most advanced script versions based on your directory
SIMULATIONS = {
    pygame.K_1: conway_kernel_FO_SLO.main,
    pygame.K_2: lenia_SLO.main,
    pygame.K_3: SIR_quarantine_TS_D_ID_Trav_SLO_AQ.main,
    pygame.K_4: two_spec_TS.main,
    pygame.K_5: rybki_fale.main,
    pygame.K_6: RPS_AS.main,
    pygame.K_7: prison.main,
    pygame.K_8: prison_TFT.main    
}

INSTRUCTIONS_TEXT = [
    "--- UNIVERSAL CONTROLS ---",
    "SPACE : Pause/Resume",
    "UP/DN : Adjust Simulation Speed (FPS)",
    "R     : Reset Grid to Initial State",
    "C     : Clear Grid completely",
    "ESC   : Return to Main Menu / Quit",
    "",
    "--- MOUSE CONTROLS ---",
    "Left Click  : Add Prey / Susceptible / Alive Cell",
    "Right Click : Add Predator / Infected / Dead Cell",
    "Middle Click: Add Wall / Quarantine / Custom Cell",
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

    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Evolution Game - Central Hub")
    clock = pygame.time.Clock()

    font_large = pygame.font.SysFont("consolas", 64, bold=True)
    font_medium = pygame.font.SysFont("consolas", 40)
    font_small = pygame.font.SysFont("consolas", 32)

    show_instructions = False

    while True:
        screen.fill(BG_COLOR)

        if show_instructions:
            render_multiline(screen, INSTRUCTIONS_TEXT, font_small, 40, 20, TEXT_COLOR)
        else:
            # Main Menu Rendering
            title = font_large.render("GAME of LIFE", True, HIGHLIGHT)
            opt1 = font_medium.render("[1] Conway Custom Kernels", True, TEXT_COLOR)
            opt2 = font_medium.render("[2] Continuous Automaton (Lenia)", True, TEXT_COLOR)
            opt3 = font_medium.render("[3] Spatial SIR Epidemic", True, TEXT_COLOR)
            opt4 = font_medium.render("[4] Lotka-Volterra Predator/Prey", True, TEXT_COLOR)
            opt5 = font_medium.render("[5] My Fish", True, TEXT_COLOR)
            opt6 = font_medium.render("[6] Rock Paper Scissors", True, TEXT_COLOR)
            opt7 = font_medium.render("[7] Spatial Prisoner's Dilemma", True, TEXT_COLOR)
            opt8 = font_medium.render("[8] Spatial Prisoner's Dilemma with memory", True, TEXT_COLOR)
            
            info = font_medium.render("Press [I] to view all controls & instructions", True, HIGHLIGHT)
            quit_opt = font_medium.render("[ESC] Quit", True, WARNING_COLOR)

            # Properly spaced coordinates to prevent overlapping
            screen.blit(title, (100, 100))
            screen.blit(opt1, (100, 220))
            screen.blit(opt2, (100, 300))
            screen.blit(opt3, (100, 380))
            screen.blit(opt4, (100, 460))
            screen.blit(opt5, (100, 540))
            screen.blit(opt6, (100, 620))
            screen.blit(opt7, (100, 700))
            screen.blit(opt8, (100, 780))

            screen.blit(info, (100, 900))
            screen.blit(quit_opt, (100, 960))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # If instructions are open, close them. Otherwise, quit.
                    if show_instructions:
                        show_instructions = False
                    else:
                        pygame.quit()
                        return
                        
                elif event.key == pygame.K_i:
                    show_instructions = not show_instructions
    
                # Launch selected script if on the main menu
                elif not show_instructions and event.key in SIMULATIONS:
                    target_function = SIMULATIONS[event.key]
    
                    # Update caption to show it is running
                    pygame.display.set_caption("Running simulation...")
    
                    # 1. Execute the imported subapp function natively
                    target_function() 
    
                    # 2. When the subapp finishes (user presses ESC in the subapp), 
                    # it returns here. Re-initialize the main menu's window dimensions and title.
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    pygame.display.set_caption("Evolution Game - Central Hub")

        clock.tick(15)

if __name__ == "__main__":
    main()
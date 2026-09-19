# Evolution Game Hub

A collection of spatial cellular automata and evolutionary game theory simulations, including Conway's Game of Life, Lenia, Lotka-Volterra, and the Iterated Prisoner's Dilemma. All simulations are unified under a single Pygame interactive hub.

## Prerequisites
* **Python 3.12** (Strictly recommended to ensure compatibility with the specific NumPy 2.4 and Pygame 2.6 rendering pipeline used in this project)
* Git

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zdebikk/Evolution_Game.git
   cd Evolution_Game


   py -3.12 -m venv .venv # Create a virtual environment
   # macOD/Linux: python3.12 -m venv .venv
   .venv\Scripts\activate # Activate the environment
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt # Install dependencies
   python main.py

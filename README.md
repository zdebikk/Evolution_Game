# Evolution Game Hub

A collection of spatial cellular automata and evolutionary game theory simulations, including Conway's Game of Life, Lenia, Lotka-Volterra, and the Iterated Prisoner's Dilemma. All simulations are unified under a single Pygame interactive hub.

## Prerequisites
* **Python 3.12** (Strictly recommended to ensure compatibility with the specific NumPy 2.4 and Pygame 2.6 rendering pipeline used in this project)

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zdebikk/Evolution_Game.git
   cd Evolution_Game

2. **Create a virtual environment:**
   ```bash
   py -3.12 -m venv .venv
   # macOD/Linux: python3.12 -m venv .venv

3. **Activate the environmenty:**
   ```bash
   .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   python main.py

## Building the executable
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico _main.py # foe the first build
   pyinstaller _main.spec # for the next builds
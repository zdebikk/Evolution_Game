import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import convolve2d
from IPython.display import HTML

# --- Setup Dimensions & Math ---
COLS, ROWS = 100, 100
KERNEL = np.array([[1, 1, 1],
                   [1, 0, 1],
                   [1, 1, 1]])

# Initialize grid
grid = np.random.choice([0, 1], size=(COLS, ROWS), p=[0.85, 0.15])

# --- Setup Plot ---
fig, ax = plt.subplots(figsize=(8, 8))
ax.axis('off')  # Hide axes for a cleaner look
# Use cmap='viridis' or 'magma' for nice colors, or 'binary' for black/white
img = ax.imshow(grid, cmap='magma', interpolation='nearest')

def update_grid(frame):
    global grid
    # Compute next generation
    neighbors = convolve2d(grid, KERNEL, mode='same', boundary='wrap')
    grid = ((neighbors == 3) | ((grid == 1) & (neighbors == 2))).astype(np.uint8)
    
    # Update image data
    img.set_data(grid)
    return [img]

# --- Render Animation ---
# frames=200 calculates 200 generations. interval=50 is the millisecond delay per frame.
anim = FuncAnimation(fig, update_grid, frames=200, interval=50, blit=True)

# Close the static plot so it doesn't render twice in Colab
plt.close()

# Display the interactive player widget
HTML(anim.to_jshtml())
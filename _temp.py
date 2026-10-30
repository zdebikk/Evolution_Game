# Maski zostawiamy jako boolean
mask_c = (grid == 1)
mask_d = (grid == 0)

neighbors_c = convolve(mask_c.astype(np.uint8), KERNEL, mode='wrap')
neighbors_d = convolve(mask_d.astype(np.uint8), KERNEL, mode='wrap')

# 2. Calculate Payoffs for every cell
payoffs = np.zeros((COLS, ROWS), dtype=float)
payoffs[mask_c] = (neighbors_c[mask_c] * R) + (neighbors_d[mask_c] * S)
payoffs[mask_d] = (neighbors_c[mask_d] * T) + (neighbors_d[mask_d] * P)

# 3. Neighborhood Imitation 
# (Find the highest scoring C and highest scoring D in the 3x3 window)
payoffs_c_only = np.where(mask_c, payoffs, -np.inf)
payoffs_d_only = np.where(mask_d, payoffs, -np.inf)

max_c_in_hood = maximum_filter(payoffs_c_only, size=3, mode='wrap')
max_d_in_hood = maximum_filter(payoffs_d_only, size=3, mode='wrap')

# The cell adopts the strategy of whoever scored highest in its neighborhood
grid[max_c_in_hood > max_d_in_hood] = 1
grid[max_d_in_hood > max_c_in_hood] = 0
# (Ties keep their current strategy)

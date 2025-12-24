import math
import matplotlib.pyplot as plt
from scipy.integrate import quad
import numpy as np

g0 = 9.82
g2 = 9.1

v = 1050

v_e = 175 * g0
mu = 7.5 * 19.423 * 6  # ~874 кг/с
m0 = 61675
dry_mass = m0 - 820 * 7.5 * 6  # масса без ускорителей

Ft = dry_mass * g2

angle = 90
rotate_time = 28
angle_per_sec = 90 / 28

def height(t):
    mt = m0 - mu * t
    if mt < dry_mass:
        return None
    return v_e * t + (v_e / mu) * mt * math.log(mt / m0) - (g0 * t ** 2) / 2

# Строим график
time = []
heights = []

curr_time = 0


for i in range(40):
    time.append(curr_time)
    h = height(curr_time)
    curr_time += 1
    heights.append(h)
print(f'height = {heights[-1]}')

total_h = (v ** 2) / (2 * g2)
h_per_sec = total_h / 30

for i in range(30):
    time.append(curr_time)
    h = heights[-1] + h_per_sec
    v -= g2
    curr_time += 1
    heights.append(h)
    print(f'{i}. height = {heights[-1]}')

# plt.plot(time, heights)
# plt.title('Зависимость высоты от времени')
# plt.grid(True, alpha = 0.3)
# plt.xlabel('Время, с')
# plt.ylabel('Высота, м')
# plt.show()
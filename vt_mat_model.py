import math
import matplotlib.pyplot as plt

time = []
speed = []

g0 = 9.82
v_e = 175 * g0
v = 0
m0 = 65175
mdry = m0 - 820 * 7.5 * 6

curr_time = 0

FUEL_MASS = 7.5 #МАССА ЕД ТОПЛИВА
FUEL_RASHOD = FUEL_MASS * 19.423 #РАСХОД ТОПЛИВА КГ/С


def dm():
    return FUEL_RASHOD * 6

while curr_time < 44:
    time.append(curr_time)
    v = v_e * math.log(abs(m0 /(m0 - dm() * curr_time))) - (g0 * curr_time)
    curr_time += 1
    speed.append(v)

for i in range(30):
    time.append(curr_time)
    curr_time += 1
    speed.append(v)


# plt.plot(time, speed)
# plt.title('Зависимость скорости от времени')
# plt.grid(True, alpha = 0.3)
# plt.xlabel('Время, s')
# plt.ylabel('Скорость, м/с')
# plt.show()
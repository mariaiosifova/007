import math
import matplotlib.pyplot as plt
from scipy.stats import alpha

#УСКОРИТЕЛИ
BOOSTER_MASS = 1500
FUEL_MASS = 7.5 #МАССА ЕД ТОПЛИВА
FUEL_RASHOD = FUEL_MASS * 19.423 #РАСХОД ТОПЛИВА КГ/С
VESSEL_MASS = 61675 #МАССА РАКЕТЫ
FUEL = 820 * FUEL_MASS * 6 #МАССА ТОПЛИВА
#УСКОРИТЕЛИ

#ФАКЕЛ
FAKEL_FUEL_MASS = 5 #МАССА ЕД ТОПЛИВА
FAKEL_OKISL_MASS = 5
FAKEL_FUEL = FAKEL_FUEL_MASS * 180
FAKEL_OKISL = FAKEL_OKISL_MASS * 220
FAKEL_FUEL_RASHOD = FAKEL_FUEL_MASS * 7.105 #РАСХОД ТОПЛИВА КГ/С
FAKEL_OKISL_RASHOD = FAKEL_OKISL_MASS * 8.684 #РАСХОД ОКИСЛИТЕЛЯ :) КГ/С
#ФАКЕЛ

time = []
mass = []

curr_time = 0 #время в секундах
curr_mass = VESSEL_MASS

while FUEL > 0:
    time.append(curr_time)
    curr_time += 1

    FUEL -= FUEL_RASHOD * 6
    mass.append(curr_mass)
    curr_mass -= (FUEL_RASHOD * 6)

curr_mass -= BOOSTER_MASS * 6
# curr_time += 1
time.append(curr_time)
mass.append(curr_mass)

for i in range(28):
    curr_time += 1
    time.append(curr_time)
    mass.append(curr_mass)

for i in range(10):
    curr_mass -= FAKEL_FUEL_RASHOD
    curr_mass -= FAKEL_OKISL_RASHOD
    curr_time += 1
    time.append(curr_time)
    mass.append(curr_mass)




#plt.plot(time, mass)
#plt.title('Зависимость массы от времени')
#plt.grid(True, alpha = 0.3)
#plt.xlabel('Время, s')
#plt.ylabel('Масса, kg')
#plt.show()
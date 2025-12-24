import json
import matplotlib.pyplot as plt

import vt_mat_model as vt

def plot_mass_vs_time(filename):
    # Чтение данных из файла
    with open(filename, 'r') as file:
        data = json.load(file)

    # Извлечение данных времени и массы
    time = [item['time'] for item in data]
    mass = [item['velocity'] for item in data]

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.plot(time, mass, 'b-', linewidth=2, label='Данные из полета в KSP')
    plt.plot(vt.time, vt.speed, 'r--', linewidth=2, label='Математическая модель', alpha=0.7)
    plt.title('Зависимость скорости от времени', fontsize=14)
    plt.xlabel('Время, с', fontsize=12)
    plt.ylabel('Скорости, м/с', fontsize=12)
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    filename = "data.json"
    plot_mass_vs_time(filename)
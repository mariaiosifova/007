import matplotlib.pyplot as plt
import krpc
import time
import math
import json
import os
from datetime import datetime

def plot_mass_vs_time(filename):
    # Чтение данных из файла
    with open(filename, 'r') as file:
        data = json.load(file)

    # Извлечение данных времени и массы
    time = [item['time'] for item in data]
    mass = [item['mass'] for item in data]

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.plot(time, mass, 'b-', linewidth=2, label='Данные из полета в KSP')
    plt.title('Зависимость массы от времени', fontsize=14)
    plt.xlabel('Время, с', fontsize=12)
    plt.ylabel('Масса, кг', fontsize=12)
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    start_flag = False
    current_datetime = datetime.now()

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    folder_name = "KSP_ZOND5_Logs"
    save_folder = os.path.join(desktop_path, folder_name)

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        print(f"Создана папка для логов: {save_folder}")

    file_timestamp = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    full_filepath = os.path.join(save_folder, f"ZOND5_flight_log_{file_timestamp}.json")

    print(f"Дата запуска: {current_datetime.strftime('%d.%m.%Y %H:%M:%S')}")
    print(f"Файл будет сохранен в: {full_filepath}")
    print("-" * 50)
    print("Попытка подключения к KSP...\n")
    try:
        conn = krpc.connect(name='Логгер для сбора данных')
        start_flag = True
    except ConnectionRefusedError:
        start_flag = False

    if start_flag:
        print("Подключено! Поиск активного корабля...\n")
        vessel = None

        while vessel is None:
            try:
                temp_vessel = conn.space_center.active_vessel
                if temp_vessel.name:
                    vessel = temp_vessel
            except Exception:
                # Если корабля нет, kRPC выбросит ошибку. Мы её ловим и ждем.
                print("Ожидание запуска ракеты...", end="\r")
                time.sleep(1)

        print(f"Логгер подключен для корабля {vessel.name}\n\n\n")

        body_ref_frame = vessel.orbit.body.reference_frame
        surface_ref_frame = vessel.surface_reference_frame
        flight_info = vessel.flight(body_ref_frame)
        latitude_stream = conn.add_stream(getattr, flight_info, 'latitude')
        longitude_stream = conn.add_stream(getattr, flight_info, 'longitude')
        velocity_stream = conn.add_stream(getattr, flight_info, 'velocity')

        vertical_speed_stream = conn.add_stream(getattr, flight_info, 'vertical_speed')
        horizontal_speed_stream = conn.add_stream(getattr, flight_info, 'horizontal_speed')

        start_lat = flight_info.latitude
        start_lon = flight_info.longitude
        body_radius = vessel.orbit.body.equatorial_radius

        time_stream = conn.add_stream(getattr, vessel, 'met')
        stream_speed = conn.add_stream(getattr, flight_info, 'speed')
        altitude_stream = conn.add_stream(getattr, flight_info, 'mean_altitude')
        stream_mass = conn.add_stream(getattr, vessel, 'mass')
        pitch_stream = conn.add_stream(getattr, flight_info, 'pitch')
        roll_stream = conn.add_stream(getattr, flight_info, 'roll')
        heading_stream = conn.add_stream(getattr, flight_info, 'heading')
        g_stream = conn.add_stream(getattr, vessel.orbit.body, 'surface_gravity')

        print(f"{"=" * 10}ЛОГГЕР ГОТОВ К РАБОТЕ{"=" * 10}\nДля начала сбора данных запустите ракету.")

        while time_stream() < 0.1:
            time.sleep(0.1)
        print(f"\n{"=" * 5} ЗАПУСК ОБНАРУЖЕН! НАЧИНАЮ ЗАПИСЬ...{"=" * 5}")

        logger_data = []
        last_print_time = time.time()
        start_real_time = time.time()

        try:
            while True:
                curr_time = time_stream()
                speed = stream_speed()
                altitude = altitude_stream()
                pitch = pitch_stream()
                mass = stream_mass()
                roll = roll_stream()
                heading = heading_stream()
                vel = velocity_stream()
                v_y = vertical_speed_stream()
                v_x = horizontal_speed_stream()

                current_lat = latitude_stream()
                current_lon = longitude_stream()

                # Вычисляем пройденное расстояние по поверхности (упрощённая формула для небольших расстояний)
                delta_lat = math.radians(current_lat - start_lat)
                delta_lon = math.radians(current_lon - start_lon)

                # Получаем гравитацию на поверхности планеты
                surface_gravity = g_stream()
                # Вычисляем гравитацию на текущей высоте (формула: g = g0 * (R/(R+h))^2)
                body_radius = vessel.orbit.body.equatorial_radius
                current_gravity = surface_gravity * (body_radius / (body_radius + altitude)) ** 2

                # Расстояние по формуле гаверсинусов (более точно) или упрощённо:
                x_pos = body_radius * math.sqrt(delta_lat ** 2 + (delta_lon * math.cos(math.radians(start_lat))) ** 2)

                y_pos = altitude  # Высота - это и есть вертикальная координата!

                vel = velocity_stream()
                vx = math.sqrt(vel[0] ** 2 + vel[2] ** 2)  # Горизонтальная составляющая скорости
                vy = vel[1]  # Вертикальная составляющая скорости

                data_point = {
                    "time": round(curr_time, 2),
                    "mass": round(mass, 2),
                    "total_speed": round(speed, 2),
                    "altitude": round(altitude, 2),
                    "pitch": round(pitch, 2),
                    "roll": round(roll, 2),
                    "heading": round(heading, 2),
                    "x_pos": round(x_pos, 2),
                    "y_pos": round(y_pos, 2),
                    "vx": round(v_x, 2),
                    "vy": round(v_y, 2),
                    "gravity": round(current_gravity, 4)
                }

                logger_data.append(data_point)

                if time.time() - last_print_time >= 1.0:
                    print(f"время:    {curr_time:.2f} с.\nвысота:   {altitude:.2f} м.\nскорость: {speed:.2f} м/с.\nнаклон:   {pitch:.2f} град.\nмасса:    {mass:.2f} кг.\n\n")
                    last_print_time = time.time()
                time.sleep(0.2)

        except KeyboardInterrupt:
            print("\nЗапись остановлена пользователем.")

        finally:
            time_stream.remove()
            stream_mass.remove()
            stream_speed.remove()
            altitude_stream.remove()
            pitch_stream.remove()
            roll_stream.remove()
            heading_stream.remove()
            latitude_stream.remove()
            longitude_stream.remove()
            velocity_stream.remove()
            g_stream.remove()
            conn.close()

            print("Сохранение данных...")
            with open(full_filepath, "w", encoding="utf-8") as f:
                json.dump(logger_data, f, indent=4)

            print(f"Файл сохранен: {full_filepath}")
            print(f"Точек записано: {len(logger_data)}")
    else:
        print("Логгер не может быть запущен. Запустите KSP и сервер kRPC!")
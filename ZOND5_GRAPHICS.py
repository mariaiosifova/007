import math
import json
import matplotlib.pyplot as plt


JSON_FILENAME = r"C:\Users\maria\Downloads\Telegram Desktop\ZOND5_flight_log_2026-02-22_15-30-29.json"

m0 = 61500.0 
cutoff_time = 42.0 
M = 5.2 * 10 ** 22 

# --- ДВИГАТЕЛИ (RT-30 "Hammer") ---
count_boosters = 6

# Тяга одного ускорителя (Ньютоны)
thrust_atm_one = 250000.0   # 250 кН (у земли)
thrust_vac_one = 300000.0   # 300 кН (в вакууме)

# Расход одного ускорителя (Единицы/с * Плотность)
# 19.423 ед/с * 7.5 кг/ед = 145.67 кг/с
flow_rate_total = 19.423 * 7.5 * count_boosters 

# --- СБРОС СТУПЕНИ ---
# Масса одного пустого = 7.65т (полная) - 6.15т (топливо) = 1.5т
mass_drop_stage = 1500.0 * count_boosters

# --- АТМОСФЕРА ---
p0 = 1.223
H = 5600   # Высота однородной атмосферы Кербина
Cx = 0.3  # Чуть снизили сопротивление, так как тяга на старте теперь меньше
S = 11.0
g0 = 9.81
R = 600000
dt = 0.1
t_max = 90.0 
G = 6.67 * 10 ** (-11)

def load_telemetry(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        t_log, m_log, h_log, v_log, vx_log, vy_log, p_log, g_log = [], [], [], [], [], [], [], []
        for entry in data:
            t_log.append(entry.get('time', 0))
            m_log.append(entry.get('mass', 0))
            h_log.append(entry.get('altitude', 0))
            v_log.append(entry.get('total_speed', 0))
            vy_log.append(entry.get('vertical_speed', entry.get('vy', 0)))
            vx_log.append(entry.get('horizontal_speed', entry.get('vx', 0)))
            p_log.append(entry.get('pitch', 0))
            g_log.append(entry.get('gravity', 9.81))
        return t_log, m_log, h_log, v_log, vx_log, vy_log, p_log, g_log
    except Exception as e:
        print(f"Ошибка: {e}")
        return [], [], [], [], [], [], []


def simulate_model():
    t = 0.0
    x, y = 0.0, 0.0
    vx, vy = 0.0, 0.0
    m = m0
    pitch_deg = 15.39
    stage_separated = False
    
    res = {'t': [], 'm': [], 'h': [], 'v': [], 'vx': [], 'vy': [], 'p': [], 'g': []}

    while t < t_max:
        # 1. РАСЧЕТ ДАВЛЕНИЯ (для тяги)
        # Отношение текущего давления к давлению на уровне моря
        # Если y=0 -> press_ratio=1. Если y=высоко -> press_ratio=0
        press_ratio = math.exp(-y / H)
        
        # 2. РАСЧЕТ ТЯГИ (ЗАВИСИТ ОТ ВЫСОТЫ!)
        # Формула интерполяции: F = F_vac - (F_vac - F_atm) * (P / P0)
        thrust_one_current = thrust_vac_one - (thrust_vac_one - thrust_atm_one) * press_ratio
        current_F_total = thrust_one_current * count_boosters

        # Если топливо кончилось (время вышло)
        if t >= cutoff_time:
            current_F_total = 0.0
            if not stage_separated:
                m -= mass_drop_stage
                stage_separated = True
        else:
            m -= flow_rate_total * dt

        # 3. ЛОГИКА УГЛА (Gravity Turn)
        if t > 5:
            if 5 < t < 10:
                turn_rate = 1.5
            elif t < 42:
                turn_rate = 0.45
            else:
                turn_rate = 1

            pitch_deg += turn_rate * dt
            if pitch_deg > 90.0: pitch_deg = 90.0
            pitch_rad = math.radians(pitch_deg)
        else:
            pitch_deg = 0
            if pitch_deg > 90.0: pitch_deg = 90.0
            pitch_rad = math.radians(pitch_deg)

        # 4. ФИЗИКА
        v_total = math.sqrt(vx ** 2 + vy ** 2)
        rho = p0 * press_ratio # Используем то же соотношение
        g = g0 * (R / (R + y)) ** 2
        
        #Fx_gravity = m * gx
        Fy_gravity = (G * m * M) / (R + y) ** 2
        F_drag = 0.5 * rho * v_total ** 2 * Cx * S
        
        Fx_thrust = current_F_total * math.sin(pitch_rad)
        Fy_thrust = current_F_total * math.cos(pitch_rad)
        
        if v_total > 0:
            Fx_drag = F_drag * (vx / v_total)
            Fy_drag = F_drag * (vy / v_total)
        else:
            Fx_drag, Fy_drag = 0, 0
        
        ax = (Fx_thrust - Fx_drag) / m
        ay = (Fy_thrust - Fy_drag - Fy_gravity) / m
        
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt
        
        res['t'].append(t); res['m'].append(m); res['h'].append(y)
        res['v'].append(v_total); res['vx'].append(vx); res['vy'].append(vy); res['p'].append(pitch_deg)
        res['g'].append(g)

    return res

# ============================================
# 5. ПОСТРОЕНИЕ ГРАФИКОВ
# ============================================
def plot_all_comparison(sim_data, log_data_tuple, filename_out="comparison_dashboard.png"):
    t_log, m_log, h_log, v_log, vx_log, vy_log, p_log, g_log = log_data_tuple
    if not t_log: t_log = [0]; m_log = [0]; h_log = [0]; v_log = [0]; vx_log = [0]; vy_log = [0]; p_log = [0]; g_log = [0]

    fig, axs = plt.subplots(3, 2, figsize=(14, 10))
    fig.suptitle(f'Сравнение модели и телеметрии ({JSON_FILENAME})', fontsize=16)

    def plot_subplot(ax, x_sim, y_sim, x_log, y_log, title, ylabel, color_sim):
        ax.plot(x_log, y_log, 'k--', label='Телеметрия', alpha=0.6, linewidth=1.5)
        ax.plot(x_sim, y_sim, color=color_sim, label='Модель', linewidth=2.5)
        ax.set_title(title, fontweight='bold')
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=8)

    plot_subplot(axs[0, 0], sim_data['t'], sim_data['m'], t_log, m_log, "Mass", "kg", "blue")
    plot_subplot(axs[0, 1], sim_data['t'], sim_data['v'], t_log, v_log, "Total Speed", "m/s", "orange")
    plot_subplot(axs[1, 0], sim_data['t'], sim_data['vx'], t_log, vx_log, "Vx (Horizontal)", "m/s", "green")
    plot_subplot(axs[1, 1], sim_data['t'], sim_data['vy'], t_log, vy_log, "Vy (Vertical)", "m/s", "red")
    plot_subplot(axs[2, 0], sim_data['t'], sim_data['h'], t_log, h_log, "Altitude", "h", "purple")
    plot_subplot(axs[2, 1], sim_data['t'], sim_data['g'], t_log, g_log, "Acceleration of gravity", "g", "purple")

    plt.xlabel("Time (s)")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

def main():
    print(f"Загрузка {JSON_FILENAME}...")
    log_data = load_telemetry(JSON_FILENAME)
    print("Расчет модели с переменной тягой (атмосфера/вакуум)...")
    sim_data = simulate_model()
    plot_all_comparison(sim_data, log_data)

if __name__ == "__main__":
    main()
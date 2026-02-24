import krpc
import time
import math

print("Подключение к серверу kRPC...")
conn = krpc.connect(name='Launch Script')
vessel = conn.space_center.active_vessel

print("Подготовка к запуску...")
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 0.0

stage_resources = vessel.resources_in_decouple_stage(stage=vessel.control.current_stage - 1, cumulative=False)
solid_fuel = stage_resources.amount('SolidFuel')
print(f"Всего топлива: {solid_fuel:.1f}")

from_minus = None
running = True

def hold_roll(target_roll, current_roll):
    if current_roll - target_roll > 5:
        vessel.control.roll = -1.0 #q
    elif current_roll - target_roll > 2 and current_roll - target_roll < 5:
        vessel.control.roll = -0.5
    elif current_roll - target_roll > 0 and current_roll - target_roll < 2:
        vessel.control.roll = -0.25

    if current_roll - target_roll < -5:
        vessel.control.roll = 1.0 #e
    elif current_roll - target_roll < -2 and current_roll - target_roll > -5:
        vessel.control.roll = 0.5
    elif current_roll - target_roll < -0 and current_roll - target_roll > -2:
        vessel.control.roll = 0.25

def hold_roll2(target_roll, current_roll):

    if abs(current_roll) < 1:
        vessel.control.yaw = 0
    else:
        if current_roll - target_roll > 5:
            vessel.control.roll = -0.075 #q
        elif current_roll - target_roll > 2 and current_roll - target_roll < 5:
            vessel.control.roll = -0.05
        elif current_roll - target_roll > 1 and current_roll - target_roll < 2:
            vessel.control.roll = -0.025

        if current_roll - target_roll < -5:
            vessel.control.roll = 0.075 #e
        elif current_roll - target_roll < -2 and current_roll - target_roll > -5:
            vessel.control.roll = 0.05
        elif current_roll - target_roll < -1 and current_roll - target_roll > -2:
            vessel.control.roll = 0.025


def hold_pitch(current_pitch):
    if current_pitch > 50:
        vessel.control.yaw = 0.5
    elif current_pitch > 10 and current_pitch < 50:
        vessel.control.yaw = -0.4
    elif current_pitch > 0 and current_pitch < 10:
        vessel.control.yaw = -0.65

def hold_pitch2(current_pitch, current_roll, start_roll):
    global from_minus, running

    if abs(current_pitch) < 1:
        vessel.control.yaw = 0
        if abs(current_roll - start_roll) < 1:
            vessel.control.yaw = 0
            vessel.control.sas = True
            running = False
    else:
        if current_pitch < -10:
            vessel.control.yaw = -0.5
            from_minus = True
        elif current_pitch > -7 and current_pitch < -3:
            from_minus = True
            vessel.control.yaw = -0.3
        elif current_pitch < -2 and current_pitch > -3:
            if from_minus == True:
                vessel.control.yaw = 0.8
            else:
                vessel.control.yaw = -0.8
        elif current_pitch < 1 and current_pitch > -2:
            if from_minus == True:
                vessel.control.yaw = 0.2
            else:
                vessel.control.yaw = -0.2

        if current_pitch > 10:
            from_minus = False
            vessel.control.yaw = 0.5
        elif current_pitch < 7 and current_pitch > 3:
            from_minus = False
            vessel.control.yaw = 0.3
        elif current_pitch > 2 and current_pitch < 3:
            if from_minus:
                vessel.control.yaw = 0.8
            else:
                vessel.control.yaw = -0.8
        elif current_pitch > 1 and current_pitch < 2:
            if from_minus:
                vessel.control.yaw = 0.2
            else:
                vessel.control.yaw = -0.2

    if abs(current_pitch) < 3:
        vessel.control.yaw = 0
        if abs(current_roll - start_roll) < 3:
            vessel.control.yaw = 0
            vessel.control.sas = True
            running = False

if __name__ == '__main__':

    print()
    vessel.control.activate_next_stage()

    vessel.control.roll = -0.26  # q

    stage_resources = vessel.resources_in_decouple_stage(stage=vessel.control.current_stage - 1, cumulative=False)
    solid_fuel = stage_resources.amount('SolidFuel')
    print(f"Всего топлива: {solid_fuel:.1f}")

    start_roll = 9999

    while solid_fuel > 0:
        current_roll = vessel.flight().roll
        current_pitch = vessel.flight().pitch

        vessel.control.yaw = 1.0

        if current_pitch < 88.5 and start_roll == 9999:
            start_roll = vessel.flight().roll
            print(f"Поворот НА СТАРТЕ: {start_roll:.2f} град.")
            vessel.control.roll = 0  # q

        if start_roll != 9999:
            relative_roll = (current_roll - start_roll)
            # print(f"Поворот: {current_roll:.2f} град.")
            print(f"Поворот от старта: {relative_roll:.2f} град.")
            hold_roll(start_roll, current_roll)

        print(f"текущйи питч: {vessel.flight().pitch:.2f} град.")

        solid_fuel = stage_resources.amount('SolidFuel')
        print(f"Всего топлива: {solid_fuel:.1f}\n")

        time.sleep(0.5)

    vessel.control.activate_next_stage()

    while vessel.flight().pitch > 6:
        current_roll = vessel.flight().roll
        current_pitch = vessel.flight().pitch

        relative_roll = (current_roll - start_roll)
        print(f"текущйи питч: {vessel.flight().pitch:.2f} град.")
        print(f"Поворот от старта: {relative_roll:.2f} град.\n")

        hold_roll2(start_roll, current_roll)
        hold_pitch(current_pitch)

    from_minus = False

    while running:
        current_pitch = vessel.flight().pitch
        current_roll = vessel.flight().roll

        relative_roll = (current_roll - start_roll)
        print(f"текущий питч: {vessel.flight().pitch:.2f} град.")
        print(f"Поворот от старта: {relative_roll:.2f} град.\n")
        print(f"Из плюса/минуса: {from_minus}")

        hold_roll2(start_roll, current_roll)
        hold_pitch2(current_pitch, current_roll, start_roll)

print('Автопилот завершил работу. Переход на ручное управление.')
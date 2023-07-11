import time
import nidaqmx
import math
import keyboard

rho = 1.15
cont = True


# Not the most elegant solution, but works to stop data reading for now.
def on_key_press(event):
    global cont
    if event.name == 'ctrl':
        cont = False


keyboard.on_press(on_key_press)


with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan("Dev1/ai6")
    while cont:
        voltage = task.read()
        # print(voltage)
        mmHg = 1.016 * voltage
        Pa = mmHg * 133.322
        windspeed = math.sqrt((2*Pa)/rho)
        print(windspeed)
keyboard.unhook_all()

print("Finished")

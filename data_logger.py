import serial
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import keyboard
from scipy import signal
import openpyxl

# Arduino set to COM5
# If this errors, switch the value next to COM with what COM port you are
# talking on.
ser = serial.Serial('COM5', 250000, timeout=1)

# ariable/Data structure initialization
# time.sleep(2)
num_pts = 10000
sr = 30000
data = deque()  # Pythons version of a linked list.
times = deque()
cont = True
start_time = time.perf_counter()
# prev_time = time.time()
i = 0

wb = openpyxl.Workbook()
ws = wb.active
last_row = ws.max_row + 1
ws.cell(row=1, column=1).value = "Time Elapsed"
ws.cell(row=1, column=2).value = "Velocity (m/s)"

fft_of_sample = None
fft_amplitudes = None
fft_phases = None
harmonics = None


# Not the most elegant solution, but works to stop data reading for now.
def on_key_press(event):
    global cont
    if event.name == 'ctrl':
        cont = False


keyboard.on_press(on_key_press)

while cont:
    elapsed_time = time.perf_counter() - start_time
    # print(elapsed_time)

    line = ser.readline()  # read a byte
    if line:
        if not line.isspace() or len(line) != 0:
            try:
                string = line.decode()  # convert byte string to unicode string
                string = string.replace('\r\n', '')
                num = round(float(string), 16)  # convert unicode string to int
                # rint(num)
                times.append(elapsed_time)
                data.append(num)
                ws.cell(row=last_row+i, column=1).value = elapsed_time
                ws.cell(row=last_row+i, column=2).value = num
                print(num)

                i += 1
            except UnicodeDecodeError:
                print('some weird stuff is happening')
                break
            except ValueError:
                continue  # Rejects bad string and continues while loop   

keyboard.unhook_all()

wb.save('PyV0100.xlsx')

print("Finished")

ser.close()

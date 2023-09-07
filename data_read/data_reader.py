import serial
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import keyboard
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Enable live graphing or \
                                  choose graphing after data collection')
parser.add_argument('--graph', action='store_true', help='Include this flag \
                    to enable live graphing of data.')
args = parser.parse_args()

# Arduino set to COM5
# If this errors, switch the value next to COM with what COM port you are
# talking on.
# ser = serial.Serial('COM5', 9600, timeout=1)

# ariable/Data structure initialization
# time.sleep(2)
num_pts = 300000
sr = 30000
data = deque()  # Pythons version of a linked list.
times = deque()
cont = True
start_time = time.perf_counter()
# prev_time = time.time()
i = 0

if args.graph:
    plt.ion()
    fig, ax = plt.subplots()
    curve, = ax.plot([], [])


# Not the most elegant solution, but works to stop data reading for now.
def on_key_press(event):
    global cont
    if event.name == 'ctrl':
        cont = False


keyboard.on_press(on_key_press)

while cont:
    elapsed_time = time.perf_counter() - start_time
    # line = ser.readline()  # read a byte
    if True:  # line:
        # string = line.decode()  # convert byte string to unicode string
        # string = string.replace('\r\n', '')
        if True:  # not string.isspace() or len(string) != 0:
            try:
                # convert unicode string to int
                num = np.sin(elapsed_time)  # round(float(string), 16)

                # append data
                times.append(elapsed_time)
                data.append(num)
                print(num)
                i += 1
            except ValueError:
                continue  # Rejects bad string and continues while loop

    # len(times) != 0 and len(data) > num_pts:
    if times[-1] - times[0] > 5 or len(data) > num_pts:
        data.popleft()
        times.popleft()

    if args.graph:
        curve.set_data(times, data)
        # Adjust the plot limits if needed
        ax.relim()
        ax.autoscale_view()
        plt.pause(0.1)

keyboard.unhook_all()
# Prints/Plots some diagnostic info to look at code behavior.
plt.plot(times, data)
plt.show()

print("Finished")

# ser.close()

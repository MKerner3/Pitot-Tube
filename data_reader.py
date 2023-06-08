import serial
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import keyboard
from scipy import signal

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
    print(elapsed_time)

    line = ser.readline()  # read a byte
    if line:
        string = line.decode()  # convert byte string to unicode string
        string = string.replace('\r\n', '')
        if not string.isspace() or len(string) != 0:
            try:
                num = round(float(string), 16)  # convert unicode string to int
                # rint(num)
                times.append(elapsed_time)
                data.append(num)
            except ValueError:
                continue  # Rejects bad string and continues while loop

            # print(len(data))

            if len(times) != 0 and len(data) > num_pts:
                data.popleft()
                times.popleft()

            Y = np.fft.fft(data)
            N = len(Y)
            n = np.arange(N)

            if times[-1] - times[0] == 0:
                sr = 1 / ((elapsed_time)/N)
                print("monke")
            else:
                sr = 1 / ((times[-1] - times[0])/N)
                print(sr)

            T = N/sr
            frequency = sr * np.arange(0, int(N/2))/N

            P2 = np.abs(Y/N)
            P1 = P2[0:int(N/2)]
            P1[1:-2] = 2*P1[1:-2]

keyboard.unhook_all()

# Prints/Plots some diagnostic info to look at code behavior.
plt.plot(times, data)
plt.show()

plt.figure(figsize=(12, 6))
plt.stem(frequency, P1, 'b',
         markerfmt=" ", basefmt="-b")
plt.xlabel('Freq (Hz)')
plt.grid()
plt.ylabel('FFT Amplitude |X(freq)|')
plt.xlim(0, 700)
plt.show()

filter_order = 10
critical_frequencies = [150]
sos = signal.butter(N=filter_order, Wn=critical_frequencies, btype='lowpass',
                    output='sos', fs=sr)
filtered = signal.sosfilt(sos, data)

Z = np.fft.fft(filtered)
S = len(Y)
s = np.arange(S)
U = S/sr
filtfreq = sr * np.arange(0, int(S/2))/S

P4 = np.abs(Z/S)
P3 = P4[0:int(S/2)]
P3[1:-2] = 2*P3[1:-2]

plt.stem(filtfreq, P3, 'g',
         markerfmt=" ", basefmt="-g")
plt.xlabel('Freq (Hz)')
plt.grid()
plt.ylabel('FFT Amplitude |X(freq)|')
plt.xlim(0, 700)
plt.show()

print("Finished")

ser.close()

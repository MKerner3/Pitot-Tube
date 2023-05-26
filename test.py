import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque
import keyboard
from scipy import signal

num_pts = 30000
sr = 30000
data = deque()
times = deque()
range = 2*np.pi
cont = True
start_time = time.perf_counter()


def freq(times):
     #2*np.pi*
     return np.sin(2*np.pi*20*times) + np.sin(2*np.pi*75*times) #period should be 1s

def on_key_press(event):
     global cont
     if event.name == 'ctrl':
          cont = False

keyboard.on_press(on_key_press)
fig = plt.figure(figsize=(9, 4))

while cont:

    current_time = time.perf_counter() - start_time
    #print(current_time)

    times.append(current_time)
    data.append(freq(current_time))
    #print(freq(current_time))
    print(len(data))

    if len(times) != 0 and len(data) > num_pts:
         data.popleft()
         times.popleft()

    end_time = current_time + 1/sr
    while time.perf_counter() < end_time:
         pass

    if len(data) == num_pts:
      data_copy = np.array(data)
      fft_of_sample = np.fft.fft(data_copy)
      fft_amplitudes = np.abs(fft_of_sample) #FIXME definitely wrong
      fft_phases = np.angle(fft_of_sample)
      harmonics = np.arange(1, 250)

keyboard.unhook_all()

plt.plot(times, data)
plt.show()
plt.bar(harmonics, fft_amplitudes[harmonics])
plt.show()


#FIXME fix filter
fc = 60
normed = fc / (sr / 2)
sos = signal.butter(N=4, Wn= fc / (40), btype='lowpass', output='sos', fs=30000)
filtered = signal.sosfilt(sos,data)
plt.plot(times, filtered)
plt.show()

print("Finished")

#TODO design method to choose cutoff frequency for excess noise
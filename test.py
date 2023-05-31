import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque
import keyboard
from scipy import signal

#Variable/Data structure initialization
num_pts = 30000
sr = 30000
data = deque()
data2 = deque()
times = deque()
range = 2*np.pi
cont = True
start_time = time.perf_counter()

# Frequency function that will be plotted against time.
def freq(times):
     #2*np.pi*
     return np.sin(2*np.pi*20*times) + np.sin(2*np.pi*75*times)

# Second frequency function that does not include the higher frequency sine wave.
# Use this to verify / compare the butterworth filter with.
def freq2(times):
    return np.sin(2*np.pi*20*times)

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
    data2.append(freq2(current_time))
    #print(freq(current_time))
    print(len(data))

    if len(times) != 0 and len(data) > num_pts:
         data.popleft()
         data2.popleft()
         times.popleft()
    
    #Match data collection rate with sampling rate
    end_time = current_time + 1/sr
    while time.perf_counter() < end_time:
         pass
    
    #Once the data reaches num_pts pts, perform fourier transform calculations on data structure.
    if len(data) == num_pts:
      data_copy = np.array(data)
      fft_of_sample = np.fft.fft(data_copy)
      fft_amplitudes = np.abs(fft_of_sample)
      fft_phases = np.angle(fft_of_sample)
      harmonics = np.arange(1, 250) #TODO maybe include more frequency ranges?

keyboard.unhook_all()

#Plots time data and fourier transform in separate plots.
#TODO figure out why all data gets printed instead of what is currently in the data array.
plt.plot(times, data)
plt.show()
plt.bar(harmonics, fft_amplitudes[harmonics])
plt.show()


#FIXME fix filter, unsure whats going on
#TODO design method to choose cutoff frequency for excess noise (fix the filter first)
fc = 60 * (2 * np.pi)
normed = fc / (sr / 2)
sos = signal.butter(N=4, Wn= fc / (40), btype='lowpass', output='sos', fs=30000)
filtered = signal.sosfilt(sos,data)
plt.plot(times, filtered)
plt.show()

plt.plot(times, data2)
plt.show()

print("Finished")


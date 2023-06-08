import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque
import keyboard
from scipy import signal

#Variable/Data structure initialization
num_pts = 3000
sr = 0
data = deque()
data2 = deque()
times = deque()
range = 2*np.pi
cont = True
start_time = time.perf_counter()
total_time = 1.5 #Total desired time interval

# Frequency function that will be plotted against time.
def freq(times):
     #2*np.pi*
     return np.sin(2*np.pi*20*times) + np.sin(2*np.pi*300*times)

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

    elapsed_time = time.perf_counter() - start_time
    #print(elapsed_time)

    times.append(elapsed_time)
    data.append(freq(elapsed_time))
    data2.append(freq2(elapsed_time))
    #print(freq(elapsed_time))
    #print(len(data))

    if len(times) != 0 and len(data) > num_pts:
         data.popleft()
         data2.popleft()
         times.popleft()
    
    Y = np.fft.fft(data)
    N = len(Y)
    n = np.arange(N)
    #times[-1] - times[0]
    if times[-1] - times[0] == 0:
      sr = 1 / ( (elapsed_time)/N )
      print("monke")
    else:
      sr = 1 / ( (times[-1] - times[0])/N )
      print(sr)
    
    T = N/sr
    frequency = sr * np.arange(0, int(N/2))/N

    P2 = np.abs(Y/N)
    P1 = P2[0:int(N/2)]
    P1[1:-2] = 2*P1[1:-2]

keyboard.unhook_all()

#Plots time data and fourier transform in separate plots.
plt.plot(times, data)
plt.show()

""""
print("Elapsed time:")
print(elapsed_time)
print()
print("Starting time:")
print(start_time)
print()
print()
print("Sampling rate:")
print(sr)
print()
print("Data length:")
print(N)
"""

plt.figure(figsize = (12,6))
plt.stem(frequency, P1, 'b', \
         markerfmt=" ", basefmt="-b")
plt.xlabel('Freq (Hz)')
plt.grid()
plt.ylabel('FFT Amplitude |X(freq)|')
plt.xlim(0,700)
plt.show()

filter_order = 10
critical_frequencies = [150]
sos = signal.butter(N=filter_order, Wn = critical_frequencies, btype='lowpass', \
                    output = 'sos', fs=sr)
filtered = signal.sosfilt(sos,data)

Z = np.fft.fft(filtered)
S = len(Y)
s = np.arange(S)
U = S/sr
filtfreq = sr * np.arange(0,int(S/2))/S

P4 = np.abs(Z/S)
P3 = P4[0:int(S/2)]
P3[1:-2] = 2*P3[1:-2]

plt.stem(filtfreq, P3, 'g', \
         markerfmt=" ", basefmt="-g")
plt.xlabel('Freq (Hz)')
plt.grid()
plt.ylabel('FFT Amplitude |X(freq)|')
plt.xlim(0,700)
plt.show()


#FIXME fix filter, unsure whats going on
#TODO design method to choose cutoff frequency for excess noise (fix the filter first)
#fc = 60 * (2 * np.pi)
#normed = fc / (sr / 2)
#sos = signal.butter(N=4, Wn= fc / (40), btype='lowpass', output='sos', fs=30000)
#filtered = signal.sosfilt(sos,data)
#plt.plot(times, filtered)
#plt.show()

#plt.plot(times, data2)
#plt.show()

print("Finished")


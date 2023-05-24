import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from collections import deque
import keyboard
from scipy import signal


data = deque()
times = deque()
num_pts = 1000
cont = True
start_time = time.time()
prev_time = time.time()
num_secs = 5


#times = np.linspace(0, 2*np.pi, num_pts)

def freq(times):
     #2*np.pi*
     return np.sin(2*np.pi*50*times) #period should be 1s

def on_key_press(event):
     global cont
     if event.name == 'ctrl':
          cont = False

keyboard.on_press(on_key_press)
fig = plt.figure(figsize=(9, 4))

while cont:

    current = time.time()
    current_time = current - start_time
    #print(current_time)
    elapsed_time = current_time - prev_time


    times.append(current_time)
    data.append(freq(current_time))
    print(freq(current_time))

    if len(data) > num_pts:
         r_head = data.popleft()

    if len(times) > num_pts:
         r_head = times.popleft()

    #https://pythonnumericalmethods.berkeley.edu/notebooks/chapter24.04-FFT-in-Python.html
    fft_of_sample = np.fft.fft(data)
    fft_amplitudes = 2.0 / num_pts * np.abs(fft_of_sample) #FIXME definitely wrong
    fft_phases = np.angle(fft_of_sample)
    harmonics = np.arange(1, 1000)

    #TODO implement the following butterworth filter
    #TODO design method to choose cutoff frequency for excess noise
    #fs = 1000
    #fc = 150
    #normed = fc / (fs / 2)
    #sos = signal.butter(N=4, Wn= fc / (40), btype='lowpass', output='sos', fs=1000)
    #filtered = signal.sosfilt(sos,f)


    #if len(fft_amplitudes) > 250:
        #plt.bar(harmonics, fft_amplitudes[harmonics])
        #plt.pause(0.001)
        #plt.cla()
     
     
    
    #plt.xlim(current_time - num_secs, current_time)    
    #plt.plot(times, data)
    #plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda val, _: f'{val:.1f}'))
    #plt.draw()
    #plt.pause(0.001)
    #plt.cla()

    #i += delta_t
    prev_time = current_time
    #time.sleep(1) #optional: add delay to reduce CPU usage

keyboard.unhook_all()




print("Finished")
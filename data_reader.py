import serial
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import keyboard

#Arduino set to COM5
#If this errors, switch the value next to COM with what COM port you are talking on.
ser = serial.Serial('COM5', 250000, timeout=1)

#Variable/Data structure initialization
#time.sleep(2)
num_pts = 10000
sr = 30000
data = deque() #Pythons version of a linked list.
times = deque()
cont = True
start_time = time.perf_counter()
#prev_time = time.time()

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
    current_time = time.perf_counter() - start_time

    times.append(current_time)

    line = ser.readline() #read a byte
    if line:
        string = line.decode() #convert byte string to unicode string
        string = string.replace('\r\n', '')
        if not string.isspace() or len(string) != 0:
            try:
                num = round(float(string), 16) #convert unicode string to int
                #print(num)
                data.append(num) 
            except ValueError:
                continue #Rejects bad string and continues while loop
            
            print(len(data))

            if len(times) != 0 and len(data) > num_pts:
                data.popleft()
                times.popleft()
            
            end_time = current_time + 1/sr
            while time.perf_counter() < end_time:
                pass

            #TODO is the fourier functionality the same with varying numbers of points?
            #data_copy = np.array(data)
            #fft_of_sample = np.fft.fft(data_copy)
            #fft_amplitudes = 2.0 / num_pts * np.abs(fft_of_sample)
            #print(len(fft_amplitudes))
            #fft_phases = np.angle(fft_of_sample)
            #harmonics = np.arange(1, 250)

            if len(data) == num_pts:
                data_copy = np.array(data)
                fft_of_sample = np.fft.fft(data_copy)
                fft_amplitudes = 2.0 / num_pts * np.abs(fft_of_sample)
                print(len(fft_amplitudes))
                fft_phases = np.angle(fft_of_sample)
                harmonics = np.arange(1, 250)

keyboard.unhook_all()

#Prints/Plots some diagnostic info to look at code behavior.
print(len(harmonics))
print(len(fft_amplitudes))
fig = plt.figure(figsize=(9, 4))
plt.bar(harmonics, fft_amplitudes[harmonics])
plt.show()

print("Finished")

ser.close()
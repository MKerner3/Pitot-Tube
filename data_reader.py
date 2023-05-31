import serial
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import keyboard

#Arduino set to COM5
#If this errors, switch the value next to COM with what COM port you are talking on.
ser = serial.Serial('COM5', 9600, timeout=1)

#Variable/Data structure initialization
#time.sleep(2)
num_pts = 10000
sr = 30000
data = deque() #Pythons version of a linked list.
times = deque()
cont = True
start_time = time.time()
prev_time = time.time()

# Not the most elegant solution, but works to stop data reading for now.
def on_key_press(event):
     global cont
     if event.name == 'ctrl':
          cont = False

keyboard.on_press(on_key_press)

while cont:
    current = time.time()
    current_time = current - start_time
    #print(current_time)
    elapsed_time = current_time - prev_time

    times.append(current_time)
    if len(times) > num_pts:
        r_head = times.popleft()

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

            #TODO Implement fourier transform calculations from test.py
            fft_of_sample = np.fft.fft(data)
            fft_amplitudes = 2.0 / num_pts * np.abs(fft_of_sample)
            print(len(fft_amplitudes))
            fft_phases = np.angle(fft_of_sample)
            harmonics = np.arange(1, 250)

        if len(data) > num_pts: #Update array with new values and delete old values
            r_head = data.popleft() #r_head temporarily stores the replaced old value.

        

        prev_time = current_time

        #TODO implement lowpass filter
        
        #fig1,ax1 = plt.subplots()
        #ax1.plot(t,data)
        #ax1.set_title('Raw data')
        
        #fig2,ax2 = plt.subplots()
        #ax2.bar(harmonics, fft_amplitudes[harmonics])
        #ax2.set_title('Fourier amplitudes of raw data')


keyboard.unhook_all()

#Prints/Plots some diagnostic info to look at code behavior.
print(len(harmonics))
print(len(fft_amplitudes))
fig = plt.figure(figsize=(9, 4))
plt.bar(harmonics, fft_amplitudes[harmonics])
plt.show()

print("Finished")

ser.close()
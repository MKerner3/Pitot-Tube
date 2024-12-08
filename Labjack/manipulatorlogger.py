"""
Demonstrates reading 2 analog inputs (AINs) in a loop from a LabJack.

Relevant Documentation:

LJM Library:
    LJM Library Installer:
        https://labjack.com/support/software/installers/ljm
    LJM Users Guide:
        https://labjack.com/support/software/api/ljm
    Opening and Closing:
        https://labjack.com/support/software/api/ljm/function-reference/opening-and-closing
    Multiple Value Functions(such as eWriteNames):
        https://labjack.com/support/software/api/ljm/function-reference/multiple-value-functions
    Timing Functions(such as StartInterval):
        https://labjack.com/support/software/api/ljm/function-reference/timing-functions

T-Series and I/O:
    Modbus Map:
        https://labjack.com/support/software/api/modbus/modbus-map
    Analog Inputs:
        https://labjack.com/support/datasheets/t-series/ain

Note:
    Our Python interfaces throw exceptions when there are any issues with
    device communications that need addressed. Many of our examples will
    terminate immediately when an exception is thrown. The onus is on the API
    user to address the cause of any exceptions thrown, and add exception
    handling when appropriate. We create our own exception classes that are
    derived from the built-in Python Exception class and can be caught as such.
    For more information, see the implementation in our source code and the
    Python standard documentation.
"""
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.io

from labjack import ljm

loopMessage = ""
if len(sys.argv) > 1:
    # An argument was passed. The first argument specifies how many times to
    # loop.
    try:
        loopAmount = int(sys.argv[1])
    except:
        raise Exception("Invalid first argument \"%s\". This specifies how many"
                        " times to loop and needs to be a number." %
                        str(sys.argv[1]))
else:
    # An argument was not passed. Loop an infinite amount of times.
    loopAmount = "infinite"
    loopMessage = " Press Ctrl+C to stop."

# Open first found LabJack
#handle = ljm.openS("ANY", "ANY", "ANY")  # Any device, Any connection, Any identifier
#handle = ljm.openS("T8", "ANY", "ANY")  # T8 device, Any connection, Any identifier
handle = ljm.openS("T7", "USB", "ANY")  # T7 device, USB connection, Any identifier
#handle = ljm.openS("T4", "ANY", "ANY")  # T4 device, Any connection, Any identifier
#handle = ljm.open(ljm.constants.dtANY, ljm.constants.ctANY, "ANY")  # Any device, Any connection, Any identifier

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

deviceType = info[0]

# Setup and call eWriteNames to configure AIN0 and AIN2 on the LabJack.
if deviceType == ljm.constants.dtT4:
    # LabJack T4 configuration

    # AIN0 and AIN2:
    #   Resolution index = Default (0)
    #   Settling, in microseconds = Auto (0)
    aNames = ["AIN0_RESOLUTION_INDEX", "AIN0_SETTLING_US",
             "AIN1_RESOLUTION_INDEX", "AIN1_SETTLING_US",
             "AIN2_RESOLUTION_INDEX", "AIN2_SETTLING_US",
             "AIN3_RESOLUTION_INDEX", "AIN3_SETTLING_US"
             ]
    aValues = [0, 0, 0, 0, 0, 0, 0, 0]
else:
    # LabJack T7 and T8 configuration

    # AIN0 and AIN2:
    #   Range: +/-10.0 V (10.0)
    #   Resolution index = Default (0)
    aNames = ["AIN0_RANGE", "AIN0_RESOLUTION_INDEX",
             "AIN1_RANGE", "AIN1_RESOLUTION_INDEX",
             "AIN2_RANGE", "AIN2_RESOLUTION_INDEX",
             "AIN3_RANGE", "AIN3_RESOLUTION_INDEX"
             ]
    aValues = [10.0, 0, 10.0, 0, 10.0, 0, 10.0, 0]

    # Negative channel and settling configurations do not apply to the T8
    if deviceType == ljm.constants.dtT7:
        #     Negative Channel = 199 (Single-ended)
        #     Settling = 0 (auto)
        aNames.extend(["AIN0_NEGATIVE_CH", "AIN0_SETTLING_US",
                       "AIN2_NEGATIVE_CH", "AIN2_SETTLING_US"])
        aValues.extend([199, 0, 199, 0])

numFrames = len(aNames)
ljm.eWriteNames(handle, numFrames, aNames, aValues)

print("\nSet configuration:")

for i in range(numFrames):
    print("    %s : %f" % (aNames[i], aValues[i]))

# Read AIN0 and AIN2 from the LabJack with eReadNames in a loop.
numFrames = 4
aNames = ["AIN0", "AIN1", "AIN2", "AIN3"]

address = 1000 # DAC0
dataType = ljm.constants.FLOAT32
stopValue = 1.0
forwardValue = 2.0
reverseValue = 3.0

print("\nStarting %s read loops.%s\n" % (str(loopAmount), loopMessage))
start_time = time.time()   # Records starting time of the loop.
intervalHandle = 1
ljm.startInterval(intervalHandle, 10000)  # Delay between readings (in microseconds)      ################# DELAY PARAMETER #################
i = 0

probedict = {}
totaldict = {}

def recordData(handle, numFrames, aNames, pos, iterations, probedict, totaldict, dir):
    probe0data = np.zeros((iterations, 1))
    probe1data = np.zeros((iterations, 1))
    probe2data = np.zeros((iterations, 1))
    probe3data = np.zeros((iterations, 1))

    for i in range(iterations):
        results = ljm.eReadNames(handle, numFrames, aNames)
        probe0data[i, 0] = results[0]
        probe1data[i, 0] = results[1]
        probe2data[i, 0] = results[2]
        probe3data[i, 0] = results[3]
        #timestamp = time.time()  # Records timestamp of data log.
        #elapsed = timestamp - start_time # Elapsed time (seconds)
    probeposdata = np.hstack([probe0data, probe1data, probe2data, probe3data])
    # TODO do differential pressure calculations here 
    if dir == 0:
        probedict[pos] = probeposdata # store in intermediate dictionary
    if dir == 1:
        probedict[29 - pos] = probeposdata # store in intermediate dictionary
    if(len(probedict)) == 30: # once intermediate dictionary has every position, transfer to total dictionary
        for j in range(len(probedict)):
            if dir == 0:
                print("Transferring slew data into slew dictionary...")
                totaldict[len(totaldict)] = probedict[j] # length of the total dictionary = index to place next value at
            if dir == 1:
                print("Transferring reverse slew data into slew dictionary...")
                totaldict[len(totaldict)] = probedict[(len(probedict) - 1) - j]
        probedict.clear() # reset intermediate dictionary


while True:
    try:
        #results = ljm.eReadNames(handle, numFrames, aNames)
        timestamp = time.time()  # Records timestamp of data log.
        elapsed = timestamp - start_time # Elapsed time (seconds)
        #print("AIN0 : %f V, AIN2 : %f V, Time : %f V" % (results[0], results[1], elapsed))
        #print("\neWriteAddress: ")
        #print("    Address - %i, data type - %i, value : %f" % (address, dataType, value))

        for j in range(30):
            print(j)
            motor_timer = time.time() # start timer
            # record data for x=200 points averaging x < 2s
            print("Logging data...")
            recordData(handle, numFrames, aNames, j, 150, probedict, totaldict, 0)
            motor_time = time.time()
            if j != 29:
                print("Finished logging. Slewing to next position.")
                ljm.eWriteAddress(handle, address, dataType, forwardValue)
                motor_time = time.time()
                while motor_time - motor_timer < 2.5:
                    motor_time = time.time()
                # when motor timer exceeds .25 seconds from data collection send off voltage
                ljm.eWriteAddress(handle, address, dataType, stopValue)
            while motor_time - motor_timer < 5:
                motor_time = time.time()
            # when timer exceeds 2 seconds continue loop
            continue
        
        '''
        for k in range(30):
            print(29 - k)
            motor_timer = time.time() # start timer
            # record data for x=200 points averaging x < 2s
            print("Logging data...")
            recordData(handle, numFrames, aNames, k, 150, probedict, totaldict, 1)
            motor_time = time.time()
            if k != 29:
                print("Finished logging. Slewing to next position.")
                ljm.eWriteAddress(handle, address, dataType, reverseValue)
                motor_time = time.time()
                while motor_time - motor_timer < 2.5:
                    motor_time = time.time()
                # when motor timer exceeds .25 seconds from data collection send off voltage
                ljm.eWriteAddress(handle, address, dataType, stopValue)
            while motor_time - motor_timer < 5:
                motor_time = time.time()
            # when timer exceeds 2 seconds continue loop
            continue
        '''

        ljm.waitForNextInterval(intervalHandle)
        if loopAmount != "infinite":
            i = i + 1
            if i >= loopAmount:
                break
    except KeyboardInterrupt:
        break
    except Exception:
        print(sys.exc_info()[1])
        break

# Close handles
ljm.cleanInterval(intervalHandle)
ljm.close(handle)

# Data Export
mat_data = {"cell_array": [totaldict[key] for key in totaldict]}

scipy.io.savemat("tare_manip_data.mat", mat_data)
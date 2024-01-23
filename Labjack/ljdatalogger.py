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

from labjack import ljm

plot1_results = []    # Results for plot 1 at the end of the loop

plot2_results = []    # Results for plot 2 at the end of the loop

time_elapsed = []     # Time from first measurement to ith measurement

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
             "AIN2_RESOLUTION_INDEX", "AIN2_SETTLING_US"]
    aValues = [0, 0, 0, 0]
else:
    # LabJack T7 and T8 configuration

    # AIN0 and AIN2:
    #   Range: +/-10.0 V (10.0)
    #   Resolution index = Default (0)
    aNames = ["AIN0_RANGE", "AIN0_RESOLUTION_INDEX",
             "AIN2_RANGE", "AIN2_RESOLUTION_INDEX"]
    aValues = [10.0, 0, 10.0, 0]

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

start_time = time.time()   # Records starting time of the loop.
for i in range(numFrames):
    print("    %s : %f" % (aNames[i], aValues[i]))

# Read AIN0 and AIN2 from the LabJack with eReadNames in a loop.
numFrames = 2
aNames = ["AIN0", "AIN2"]

print("\nStarting %s read loops.%s\n" % (str(loopAmount), loopMessage))
intervalHandle = 1
ljm.startInterval(intervalHandle, 10000)  # Delay between readings (in microseconds)      ################# DELAY PARAMETER #################
i = 0
while True:
    try:
        results = ljm.eReadNames(handle, numFrames, aNames)
        timestamp = time.time()  # Records timestamp of data log.
        elapsed = timestamp - start_time # Elapsed time (seconds)
        print("AIN0 : %f V, AIN2 : %f V" % (results[0], results[1]))
        plot1_results.append(results[0])
        plot2_results.append(results[1])
        time_elapsed.append(elapsed)
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

#================================================Data Handling================================================#

# Plot data
plt.plot(time_elapsed, plot1_results, label = 'AIN0 Output')
plt.plot(time_elapsed, plot2_results, label = 'AIN2 Output')
plt.xlabel('Elapsed Time (seconds)')
plt.ylabel('Voltage (V)')
plt.legend()
plt.show()
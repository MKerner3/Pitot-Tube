# Pyqt test script for real time plotting.

import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from labjack import ljm
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.xsize = 50   # Specifies the amount of data points shown
        # dynamic plot
        self.plot_graph = pg.PlotWidget()
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground("w")
        pen = pg.mkPen(color=(255, 0, 0))
        #self.plot_graph.setTitle("Placeholder", color="b", size="20pt")
        styles = {"color": "red", "font-size": "18px"}
        self.plot_graph.setLabel("left", "Data", **styles)
        self.plot_graph.setLabel("bottom", "Time", **styles)
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.setYRange(2.5,3.3)
        self.time = [0] * self.xsize
        self.ain1data = [0] * self.xsize
        self.ain2data = [0] * self.xsize
        # Get a line reference
        self.line0 = self.plot_graph.plot(
            self.time,
            self.ain1data,
            name="Sensor 0",
            pen=pen,
            symbol="o",
            symbolSize=15,
            symbolBrush="b",
        )

        self.line1 = self.plot_graph.plot(
            self.time,
            self.ain2data,
            name="Sensor 1",
            pen=pen,
            symbol="x",
            symbolSize=15,
            symbolBrush="r",
        )

        # Add a timer to simulate new ain1data measurements
        self.timer = QtCore.QTimer()
        self.timer.setInterval(0) # Delay between readings (in milliseconds)      ################# DELAY PARAMETER #################
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        global loop_counter
        intervalHandle = 1
        ljm.startInterval(intervalHandle, 10000)  # Delay between readings (in microseconds)      ################# DELAY PARAMETER #################
        try:
            results = ljm.eReadNames(handle, numFrames, aNames)
            timestamp = time.time()  # Records timestamp of data log.
            elapsed = timestamp - start_time # Elapsed time (seconds)
            print("AIN0 : %f V, AIN2 : %f V" % (results[0], results[1]))
            # Store updated values
            plot1_results.append(results[0])
            plot2_results.append(results[1])
            time_elapsed.append(elapsed)
            
            # Plot updates values on graph on graph
            self.time = self.time[1:]
            self.time.append(elapsed)
            self.ain1data = self.ain1data[1:]
            self.ain1data.append(results[0])

            self.ain2data = self.ain2data[1:]
            self.ain2data.append(results[1])

            self.line0.setData(self.time, self.ain1data)
            self.line1.setData(self.time, self.ain2data)
            
            ljm.waitForNextInterval(intervalHandle)
            if loopAmount != "infinite":
                loop_counter = loop_counter + 1
                if loop_counter >= loopAmount:
                    print("Break: Loop Amount Reached!")
                    sys.exit()
        except Exception:
            print(sys.exc_info()[1])
            print("Break: Exception!")
            sys.exit()


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
    loopMessage = " Exit plot window to stop."

loop_counter = 0 # loop counter

# Open first found LabJack
handle = ljm.openS("T7", "USB", "ANY")  # T7 device, USB connection, Any identifier

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

for i in range(numFrames):
    print("    %s : %f" % (aNames[i], aValues[i]))

# Read AIN0 and AIN2 from the LabJack with eReadNames in a loop.
numFrames = 2
aNames = ["AIN0", "AIN2"]

print("\nStarting %s read loops.%s\n" % (str(loopAmount), loopMessage))
start_time = time.time()   # Records starting time of the loop.

app = QtWidgets.QApplication([])
main = MainWindow()
main.show()
sys.exit(app.exec_())
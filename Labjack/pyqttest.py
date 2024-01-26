# Pyqt test script for real time plotting.

from random import randint
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # dynamic plot
        self.plot_graph = pg.PlotWidget()
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground("w")
        pen = pg.mkPen(color=(255, 0, 0))
        #self.plot_graph.setTitle("Placeholder", color="b", size="20pt")
        styles = {"color": "red", "font-size": "18px"}
        self.plot_graph.setLabel("left", "Data", **styles)
        self.plot_graph.setLabel("bottom", "Time", **styles)
        #self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.setYRange(0,40)
        self.time = [0] * 50
        self.temperature = [0] * 50   ####==================================####
        # Get a line reference
        self.line = self.plot_graph.plot(
            self.time,
            self.temperature,
            name="Sensor",
            pen=pen,
            symbol="+",
            symbolSize=15,
            symbolBrush="b",
        )


        # Add a timer to simulate new temperature measurements
        self.timer = QtCore.QTimer()
        self.timer.setInterval(0) # Delay between readings (in milliseconds)      ################# DELAY PARAMETER #################
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        self.time = self.time[1:]
        self.time.append(self.time[-1] + 1)
        self.temperature = self.temperature[1:]
        self.temperature.append(randint(20, 40)) ####==================================####
        self.line.setData(self.time, self.temperature)

app = QtWidgets.QApplication([])
main = MainWindow()
main.show()
app.exec()
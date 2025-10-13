import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQtGraph Example")

        # Create the plot widget
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)

        # Configure plot
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Time')
        self.plot_widget.addLegend()
        self.plot_widget.setBackground('black')

        # Create a plot item
        self.curve = self.plot_widget.plot(
            pen=pg.mkPen('y', width=2),
            name="Signal"
        )

        self.lin = pg.LinearRegionItem()
        self.lin.sigRegionChanged.connect(self.lol)
        self.plot_widget.addItem(self.lin)

        # Generate data
        self.x = np.linspace(0, 2*np.pi, 100)
        self.phase = 0
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)  # update every 50 ms

    def update_plot(self):
        y = np.sin(self.x + self.phase)
        self.curve.setData(self.x, y)
        self.phase += 0.1

    def lol(self):
        print("hehehehe")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    sys.exit(app.exec())

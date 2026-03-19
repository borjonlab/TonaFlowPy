import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QFrame, QFileDialog, QMessageBox, QLineEdit, QGroupBox,
    QHBoxLayout, QGridLayout, QToolBar, QMenuBar
)
from PyQt6.QtCore import Qt

from PyQt6.QtGui import QPalette, QColor, QAction, QKeySequence, QPixmap

import pyqtgraph as pg
from ECG_controller import ECG_controller

from widgets import EcgPlot, HeartRatePlot




class ECGApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = ECG_controller(self)
        # Set up the events from the controller
        # self.setup_events()

        self.setWindowTitle("TonaFlow")
        self.setGeometry(100, 100, 1800, 720)
        self.set_dark_theme()
        self.setup_ui()
        self.setup_menubar()



    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(38, 38, 38))
        palette.setColor(QPalette.ColorRole.Text, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        self.setPalette(palette)



    def setup_ui(self):
        """Set up the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left side - Plots
        self.setup_plot_area(main_layout)

        # Right side - Controls
        self.setup_control_panel(main_layout)

    def setup_plot_area(self, main_layout):
        """Set up the plotting area on the left side"""
        plot_frame = QFrame()
        plot_layout = QVBoxLayout(plot_frame)

        # Main ECG plot
        # self.main_graph = pg.PlotWidget()
        self.main_graph = EcgPlot()
        self.main_graph.setTitle("ECG Signal")
        self.main_graph.setLabel('left', "Amplitude")
        self.main_graph.setLabel('bottom', "Time (s)")
        self.main_graph.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.main_graph)

        # Heart rate plot
        self.hr_graph = HeartRatePlot()

        # Link hr_graph with main_graph on the x axis
        pl = self.hr_graph.getPlotItem()
        vb = pl.getViewBox()
        vb.setXLink(self.main_graph)

        self.hr_graph.setTitle("Heart Rate")
        self.hr_graph.setLabel('left', "BPM")
        self.hr_graph.setLabel('bottom', "Time (s)")
        self.hr_graph.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.hr_graph)

        main_layout.addWidget(plot_frame, 2)

    def setup_control_panel(self, main_layout):
        """Set up the control panel on the right side"""
        control_frame = QFrame()
        control_layout = QVBoxLayout(control_frame)
        control_frame.setMaximumWidth(360)

        # Heartbeat controls
        self.setup_heartbeat_controls(control_layout)

        # Data removal controls
        self.setup_removal_controls(control_layout)

        # View controls
        self.setup_view_controls(control_layout)

        # Session info
        self.setup_session_info(control_layout)

        # Beat detection controls
        # self.setup_detection_controls(control_layout)

        # Chart controls
        # self.setup_chart_controls(control_layout)

        # Coordinates display
        self.coordinates_display = QLabel("(x, y) = (—, —)")
        self.coordinates_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.coordinates_display.setStyleSheet(
            "background-color: #F0F0F0; color: #000000; padding: 5px; border-radius: 3px;"
        )
        control_layout.addWidget(self.coordinates_display)

        self.logo = QLabel()
        pixmap = QPixmap('./imgs/TF Logo Darkmode.png')
        self.logo.setScaledContents(True)
        self.logo.setPixmap(pixmap.scaled(200,200))
        # main_layout.addWidget(self.logo)
        control_layout.addWidget(self.logo)

        control_layout.addStretch()
        main_layout.addWidget(control_frame, 1)

        


        # Tonaflow image? 

    def setup_menubar(self):
        menubar = self.menuBar()
        # File menu, new
        file_menu = menubar.addMenu('File...')

        load_ecg_action = QAction("Load ECG File (.csv)", self)
        # load_ecg_action.triggered.connect(self.load_csv_data)
        load_ecg_action.triggered.connect(self.controller.load_data)

        export_data_action = QAction("Export Data (.csv)", self)
        export_data_action.setShortcut(QKeySequence("Ctrl+S"))
        export_data_action.triggered.connect(self.export_csv)

        file_menu.addAction(load_ecg_action)
        file_menu.addAction(export_data_action)

        ecg_menu = menubar.addMenu('ECG...')
        filter_ecg_action = QAction("Filter ECG (CWT)", self)
        filter_ecg_action.triggered.connect(self.launch_filter_ecg)

        detect_beats_action = QAction("Detect Heartbeats", self)
        detect_beats_action.triggered.connect(self.launch_beat_detection)

        ecg_menu.addAction(filter_ecg_action)
        ecg_menu.addAction(detect_beats_action)

    def setup_heartbeat_controls(self, layout):
        """Set up heartbeat control group"""
        heartbeat_group = QGroupBox("Heartbeats")
        hb_layout = QVBoxLayout(heartbeat_group)

        add_btn = QPushButton("Add Heartbeat")
        add_btn.clicked.connect(self.add_heartbeat)
        hb_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove Heartbeat")
        remove_btn.clicked.connect(self.remove_heartbeat)
        hb_layout.addWidget(remove_btn)

        layout.addWidget(heartbeat_group)

    def setup_removal_controls(self, layout):
        """Set up data removal control group"""
        removal_group = QGroupBox("Data Removal")
        removal_layout = QVBoxLayout(removal_group)

        insert_removal_region_btn = QPushButton("Insert Removal Region")
        insert_removal_region_btn.clicked.connect(self.insert_removal_region)
        removal_layout.addWidget(insert_removal_region_btn)

        layout.addWidget(removal_group)

    def setup_view_controls(self, layout):
        """Set up view control group"""
        view_group = QGroupBox("View")
        view_layout = QVBoxLayout(view_group)

        self.show_raw_checkbox = QCheckBox("Show Raw Signal")
        self.show_raw_checkbox.setChecked(False)
        self.show_raw_checkbox.checkStateChanged.connect(self.show_raw_checked)
        view_layout.addWidget(self.show_raw_checkbox)

        self.show_partial_checkbox = QCheckBox("Show Partial Calculation Area")
        self.show_partial_checkbox.setChecked(True)
        view_layout.addWidget(self.show_partial_checkbox)

        # upload_btn = QPushButton("Upload ECG Data")
        # upload_btn.clicked.connect(self.load_csv_data)
        # view_layout.addWidget(upload_btn)

        layout.addWidget(view_group)

    def setup_session_info(self, layout):
        """Set up session information display"""
        info_group = QGroupBox("Session Info")
        info_layout = QVBoxLayout(info_group)

        self.session_length_label = QLabel("Session Length (s): —")
        info_layout.addWidget(self.session_length_label)

        self.sampling_rate_label = QLabel("Sampling Rate (Hz): —")
        info_layout.addWidget(self.sampling_rate_label)

        self.filename_label = QLabel("Filename: —")
        info_layout.addWidget(self.filename_label)

        self.filepath_label = QLabel("Filepath: —")
        info_layout.addWidget(self.filepath_label)

        layout.addWidget(info_group)

    def add_heartbeat(self):
        self.controller.add_heartbeat()

    def remove_heartbeat(self):
        self.controller.remove_heartbeat()

    def insert_removal_region(self):
        self.controller.insert_removal_region()

    def draw_removal_interval(self):
        """Placeholder for draw removal interval functionality"""
        QMessageBox.information(self, "Draw Interval", "Draw removal interval functionality would be implemented here")

    def launch_beat_detection(self):
        """Launch the beat detection window"""
        self.controller.open_beat_detection()
    
    def show_raw_checked(self):
        self.controller.show_raw_checked()

    def launch_filter_ecg(self):
        """Launch the filter ECG window"""
        self.controller.open_filter_ecg()

    def export_csv(self):
        self.controller.export_csv()

    def reset_to_original_data(self):
        """Placeholder for reset functionality"""
        QMessageBox.information(self, "Reset", "Reset to original data functionality would be implemented here")

    def start_chart(self):
        """Placeholder for start chart functionality"""
        QMessageBox.information(self, "Start Chart", "Start chart functionality would be implemented here")

    def stop_chart(self):
        """Placeholder for stop chart functionality"""
        QMessageBox.information(self, "Stop Chart", "Stop chart functionality would be implemented here")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # controller = ECG_controller()
    window = ECGApplication()
    window.show()

    sys.exit(app.exec())


# if __name__ == "__main__":
#     with cProfile.Profile() as pr:
#         main()
#     ps = pstats.Stats(pr).sort_stats(SortKey.CUMULATIVE)
#     ps.strip_dirs()
#     ps.print_stats()
# if __name__ == "__main__":
def main():
    import cProfile
    import pstats
    from pstats import SortKey
    import io

    pr = cProfile.Profile()
    pr.enable()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = ECGApplication()
    window.show()

    exit_code = app.exec()  # this blocks until window is closed

    pr.disable()

    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(sortby)
    ps.print_stats(30)  # top 30 functions
    print(s.getvalue())

    sys.exit(exit_code)


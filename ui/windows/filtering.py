from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QFrame, QLineEdit, QGroupBox,
    QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt

import pyqtgraph as pg


class FilteringWindow(QWidget):
    settingsChanged = pyqtSignal(dict)
    analysisRun = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.parent = parent
        self.setWindowTitle("ECG Filter Settings")
        self.setGeometry(100, 100, 1500, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        
        self.setup_ui()
        self.initialize_plot_items()
        self.applyStyles()
        self.connect_signals()
        

    def connect_signals(self):
        self.cutlower.textChanged.connect(self.emit_settings)
        self.cutUpper.textChanged.connect(self.emit_settings)

    def emit_settings(self):
        """Collect current settings and emit as dict"""
        try:
            settings = self.get_all_settings()
            self.settingsChanged.emit(settings)
        except ValueError:
            pass  # Ignore incomplete inputs

    def get_all_settings(self):
        settings = {
            "low_cutoff": float(self.cutlower.text()),
            "high_cutoff": float(self.cutUpper.text())
        }
        return settings

    def initialize_plot_items(self):
        filtpen = pg.mkPen(color = 'r', width = 3)
        ## Filter Plot
        self.ECG_line = pg.PlotDataItem(name = "Raw ECG")
        self.filtered_ecg_line = pg.PlotDataItem(pen = filtpen, name = "Filtered ECG")

        self.ecg_display.addItem(self.ECG_line)
        self.ecg_display.addItem(self.filtered_ecg_line)


    def applyStyles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QGroupBox {
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                background-color: #2D2D2D;
                border: 2px solid #404040;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
                color: #CCCCCC;
                left: 10px;
            }
            QPushButton {
                border-radius: 4px;
                font-weight: bold;
                background-color: #404040;
                border: none;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover { background-color: #505050; }
            QPushButton:pressed { background-color: #303030; }
            QLineEdit, QComboBox {
                background-color: #2D2D2D;
                border: 2px solid #505050;
                padding: 6px;
                color: #FFFFFF;
                border-radius: 4px;
            }
            QLabel {
                font-weight: bold;
                font-size: 12px;
            }
        """)

    
    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #404040;
                border-radius: 10px;
                background-color: #2D2D2D;
                padding: 10px;
            }
        """)
        control_frame.setMaximumWidth(300)
        control_layout = QVBoxLayout(control_frame)

        close_button = QPushButton("✕")
        close_button.clicked.connect(self.close)
        control_layout.addWidget(close_button)

        header = QLabel("ECG Filter Settings")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 16px; padding: 8px;")
        control_layout.addWidget(header)

        filter_box = QGroupBox("Filter Settings")
        filter_layout = QVBoxLayout(filter_box)


        self.cutlower = QLineEdit("30")
        self.cutUpper = QLineEdit("40")
        filter_layout.addWidget(QLabel("Lower Cutoff"))
        filter_layout.addWidget(self.cutlower)
        filter_layout.addWidget(QLabel("Upper Cutoff"))
        filter_layout.addWidget(self.cutUpper)

        control_layout.addWidget(filter_box)

        analyze_btn = QPushButton("Filter")
        analyze_btn.clicked.connect(self.run_analysis)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        control_layout.addWidget(analyze_btn)
        control_layout.addWidget(cancel_btn)
        control_layout.addStretch()

        graph_frame = QFrame()
        graph_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #404040;
                border-radius: 10px;
                padding: 10px;
            }
        """)

        graph_layout = QHBoxLayout(graph_frame)

        # Left graphs (stacked)
        left_graph_layout = QVBoxLayout()

        self.ecg_display = pg.PlotWidget(title="ECG")
        self.ecg_display.setLabel('left', 'Amplitude')
        self.ecg_display.setLabel('bottom', 'Time (s)')
        self.ecg_display.showGrid(x=True, y=True, alpha=0.3)
        self.ecg_display.setBackground("#252525")
        leg = self.ecg_display.addLegend()
        
        # self.filtered_ecg_display = pg.PlotWidget(title="Filtered ECG")
        # self.filtered_ecg_display.setLabel('left', 'Amplitude')
        # self.filtered_ecg_display.setLabel('bottom', 'Time (s)')
        # self.filtered_ecg_display.showGrid(x=True, y=True, alpha=0.3)
        # self.filtered_ecg_display.setBackground('#1A252F')

        left_graph_layout.addWidget(self.ecg_display)
        # left_graph_layout.addWidget(self.filtered_ecg_display)


        graph_layout.addLayout(left_graph_layout, stretch=2)






        main_layout.addWidget(control_frame)
        main_layout.addWidget(graph_frame)

    def run_analysis(self):
        ecg = getattr(self.parent.controller, 'ecg', None)
        if ecg.HeartBeats is not None:
            reply = QMessageBox.question(self.parent,"Alert","Beat analysis already run. Re-filtering will require beat analysis to be run again. Run filtering?",QMessageBox.StandardButton.Yes,QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                settings = self.get_all_settings()
                self.analysisRun.emit(settings)
        else:
            settings = self.get_all_settings()
            self.analysisRun.emit(settings)

    def update_ecg_display(self):
        if self.parent and hasattr(self.parent, 'controller'):
            ecg = getattr(self.parent.controller, 'ecg', None)
            if ecg and ecg.X_Data is not None and ecg.Y_Data is not None:
                self.ECG_line.setData(ecg.X_Data, ecg.Y_Data)
                self.filtered_ecg_line.setData(ecg.X_Data, ecg.Y_Data)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_ecg_display()

    def close(self):
        self.hide()

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QFrame, QLineEdit, QGroupBox,
    QHBoxLayout
)
import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt

class BeatDetectionWindow(QWidget):

    settingsChanged = pyqtSignal(dict)
    analysisRun = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.setWindowTitle("Beat Detection Settings")
        self.setGeometry(100, 100, 1500, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.apply_styles()
        self.setup_ui()

        self.connect_signals()
        self.initialize_plot_items()

    def initialize_plot_items(self):
        self.ECG_line = pg.PlotDataItem()
        self.threshold_line = pg.PlotDataItem(pen='r',width = 3)
        self.ecg_display.addItem(self.ECG_line)
        self.ecg_display.addItem(self.threshold_line)
        pass

    def connect_signals(self):
        # Connect inputs to emit signal whenever they change
        self.window_input.textChanged.connect(self.emit_settings)
        self.percentile_input.editingFinished.connect(self.emit_settings)
        self.abs_check.stateChanged.connect(self.emit_settings)
        self.conv_win_input.textChanged.connect(self.emit_settings)
        

    def emit_settings(self):
        """Collect current settings and emit as dict"""
        try:
            settings = self.get_all_settings()
            self.settingsChanged.emit(settings)
        except ValueError:
            pass  # Ignore incomplete inputs

    def apply_styles(self):
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
                color: #FFFFFF;
                background-color: #2D2D2D;
                border: 2px solid #404040;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px 0 5px;
                color: #CCCCCC;
                left: 10px;
                font-weight: bold;
            }
            QPushButton {
                border-radius: 4px;
                font-weight: bold;
                background-color: #404040;
                border: none;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
            QLineEdit {
                background-color: #2D2D2D;
                border: 2px solid #505050;
                padding: 6px;
                color: #FFFFFF;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border-color: #808080;
            }
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #505050;
                border-radius: 3px;
                background-color: #2D2D2D;
            }
            QCheckBox::indicator:checked {
                background-color: #808080;
                border-color: #808080;
            }
            QLabel {
                color: #FFFFFF;
                font-weight: bold;
                font-size: 12px;
            }
        """)

    def setup_ui(self):
        # Close button
        close_button = QPushButton("✕")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                border: none;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 12px;
                min-width: 20px;
                max-width: 20px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
        """)
        close_button.clicked.connect(self.close)

        # Main layout
        layout = QHBoxLayout()

        # Left side - Controls
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {                
                border: 2px solid #404040;
                border-radius: 10px;
                background-color: #2D2D2D;
                padding: 10px;
            }
        """)
        control_layout = QVBoxLayout()

        control_layout.addWidget(close_button)
        control_layout.addSpacing(5)

        header = QLabel("Beat Detection Settings")
        header.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-weight: bold;
                font-size: 16px;
                padding: 8px;
                border-bottom: 2px solid #404040;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(header)
        control_layout.addSpacing(10)

        # Threshold Settings Group
        thresh_box = QGroupBox("Threshold Settings")
        thresh_box_layout = QVBoxLayout()

        # Window setting
        win_layout = QHBoxLayout()
        win_lbl = QLabel("Threshold Window (sec):")
        win_lbl.setStyleSheet("min-width: 150px;")
        win_layout.addWidget(win_lbl)
        self.window_input = QLineEdit("5.0")
        self.window_input.setMaximumWidth(100)
        win_layout.addWidget(self.window_input)
        thresh_box_layout.addLayout(win_layout)

        # Percentile setting
        perc_layout = QHBoxLayout()
        perc_lbl = QLabel("Threshold Percentile:")
        perc_lbl.setStyleSheet("min-width: 150px;")
        perc_layout.addWidget(perc_lbl)
        self.percentile_input = QLineEdit("95.0")
        self.percentile_input.setMaximumWidth(100)
        perc_layout.addWidget(self.percentile_input)
        thresh_box_layout.addLayout(perc_layout)

        self.abs_check = QCheckBox("Use Absolute Value")
        self.abs_check.setChecked(False)
        thresh_box_layout.addWidget(self.abs_check)

        thresh_box.setLayout(thresh_box_layout)
        control_layout.addWidget(thresh_box)

        # Heart Rate Calculation Group
        hr_calc_box = QGroupBox("Heart Rate Calculation Settings")
        hr_calc_layout = QVBoxLayout()

        conv_win_layout = QHBoxLayout()
        conv_win_lbl = QLabel("Convolution Window Size:")
        conv_win_lbl.setStyleSheet("min-width: 150px;")
        conv_win_layout.addWidget(conv_win_lbl)
        self.conv_win_input = QLineEdit("10")
        self.conv_win_input.setMaximumWidth(100)
        conv_win_layout.addWidget(self.conv_win_input)
        hr_calc_layout.addLayout(conv_win_layout)

        hr_calc_box.setLayout(hr_calc_layout)
        control_layout.addWidget(hr_calc_box)


        # Action buttons
        button_layout = QHBoxLayout()
        analyze_btn = QPushButton("Run Analysis")
        analyze_btn.clicked.connect(self.run_analysis)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        button_layout.addWidget(analyze_btn)
        button_layout.addWidget(cancel_btn)
        control_layout.addLayout(button_layout)

        control_layout.addStretch()
        control_frame.setLayout(control_layout)
        control_frame.setMaximumWidth(300)

        # Right side - Graph area
        graph_frame = QFrame()
        graph_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 2px solid #404040;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        graph_layout = QVBoxLayout()

        # ECG Preview plot
        self.ecg_display = pg.PlotWidget()
        self.ecg_display.setTitle("ECG Preview")
        self.ecg_display.setLabel('left', 'Amplitude')
        self.ecg_display.setLabel('bottom', 'Time (s)')
        self.ecg_display.showGrid(x=True, y=True, alpha=0.3)
        self.ecg_display.setBackground('#252525')

        # Heart Rate Preview plot
        # self.hr_display = pg.PlotWidget()
        # self.hr_display.setTitle("Heart Rate Preview")
        # self.hr_display.setLabel('left', 'BPM')
        # self.hr_display.setLabel('bottom', 'Time (s)')
        # self.hr_display.showGrid(x=True, y=True, alpha=0.3)
        # self.hr_display.setBackground('#1A252F')

        graph_layout.addWidget(self.ecg_display)
        # graph_layout.addWidget(self.hr_display)
        graph_frame.setLayout(graph_layout)

        layout.addWidget(control_frame)
        layout.addWidget(graph_frame)
        self.setLayout(layout)

    def get_all_settings(self):
        settings = {
            "window": float(self.window_input.text()),
            "percentile": float(self.percentile_input.text()),
            "use_abs": self.abs_check.isChecked(),
            "conv_win": int(self.conv_win_input.text())
        }
        return settings

    def run_analysis(self):
        settings = self.get_all_settings()
        self.analysisRun.emit(settings)

    def close(self):
        self.hide()



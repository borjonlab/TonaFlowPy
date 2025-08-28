import sys
import os
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import  QApplication
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QHBoxLayout


from PyQt6.QtWidgets import QGridLayout



from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

import pyqtgraph as pg


try:
    import ECG_ModPyQt
    from ECG_ModPyQt import ECGProcessor
except Exception as e:
    class ECGProcessor:
        def __init__(self, x, y, fs):
            self.X_Data = np.asarray(x) if x is not None else None
            self.Y_Data = np.asarray(y) if y is not None else None
            self.SamplingRate = fs if fs else np.nan
            self.HeartBeats = None
            self.HeartRate_X = None
            self.HeartRate_Y = None
            self.Thresholds = None
            self.Thresholds_X = None

        def analysis_results(self, ecg_widget=None, hr_widget=None, threshold_percentile=95.0, threshold_window=5.0):
            if self.X_Data is None or self.Y_Data is None or self.X_Data.size != self.Y_Data.size:
                return

            perc = np.nanpercentile(np.abs(self.Y_Data), threshold_percentile)
            beats_mask = np.where(np.abs(self.Y_Data) >= perc, 1, 0)
            self.HeartBeats = beats_mask

            if self.SamplingRate and np.isfinite(self.SamplingRate):
                win_s = max(1.0, float(threshold_window))
                win_n = int(self.SamplingRate * win_s)
                if win_n < 1:
                    win_n = 1
                rolling = np.convolve(beats_mask, np.ones(win_n, dtype=float), mode="same")
                hr_bpm = (rolling / win_s) * 60.0
                self.HeartRate_X = self.X_Data
                self.HeartRate_Y = hr_bpm

            if ecg_widget is not None:
                ecg_widget.clear()
                ecg_widget.plot(self.X_Data, self.Y_Data, pen=pg.mkPen(color=(0, 120, 255)), linewidth=2, label="ECG")
                hb_idx = np.where(beats_mask == 1)[0]
                if hb_idx.size:
                    ecg_widget.plot(self.X_Data[hb_idx], self.Y_Data[hb_idx],
                                    pen=None, symbol='o', symbolSize=7, symbolBrush='r', label="Detected Beats")

            if hr_widget is not None:
                hr_widget.setTitle("Heart Rate Preview")


class BeatDetectionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Beat Detection Settings")
        self.setGeometry(100, 100, 800, 600)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            QGroupBox {
                background-color: #2D2D2D;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #CCCCCC;
                font-weight: bold;
            }
            QPushButton {
                background-color: #404040;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
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
        
        self.setup_ui()

    def setup_ui(self):
        x_buttotn = QPushButton("✕")
        x_buttotn.setStyleSheet("""
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
        x_buttotn.clicked.connect(self.transfer_and_exit)
        
        # Main layout
        layout = QHBoxLayout()

        # Left side - Controls
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border: 2px solid #404040;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        control_layout = QVBoxLayout()
        
        control_layout.addWidget(x_buttotn)
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

        thresh_box = QGroupBox("Threshold Settings")
        thresh_box_layout = QVBoxLayout()

        win_layout = QHBoxLayout()
        win_lbl = QLabel("Threshold Window (sec):")
        win_lbl.setStyleSheet("""
            QLabel {
                color: #FFFFFF !important;
                font-weight: bold !important;
                font-size: 12px !important;
                background-color: transparent !important;
                min-width: 150px !important;
            }
        """)
        win_layout.addWidget(win_lbl)
        self.window_input = QLineEdit("5.0")
        self.window_input.setMaximumWidth(100)
        win_layout.addWidget(self.window_input)
        thresh_box_layout.addLayout(win_layout)
        thresh_box_layout.addSpacing(5)

        perc_layout = QHBoxLayout()
        perc_lbl = QLabel("Threshold Percentile:")
        perc_lbl.setStyleSheet("""
            QLabel {
                color: #FFFFFF !important;
                font-weight: bold !important;
                font-size: 12px !important;
                background-color: transparent !important;
                min-width: 150px !important;
            }
        """)
        perc_layout.addWidget(perc_lbl)
        self.percentile_input = QLineEdit("95.0")
        self.percentile_input.setMaximumWidth(100)
        perc_layout.addWidget(self.percentile_input)
        thresh_box_layout.addLayout(perc_layout)

        self.abs_check = QCheckBox("Use Absolute Value")
        self.abs_check.setChecked(True)
        thresh_box_layout.addWidget(self.abs_check)

        thresh_box.setLayout(thresh_box_layout)
        control_layout.addWidget(thresh_box)
        control_layout.addSpacing(10)

        hr_calc_box = QGroupBox("Heart Rate Calculation Settings")
        hr_calc_layout = QVBoxLayout()

        conv_win_layout = QHBoxLayout()
        conv_win_lbl = QLabel("Convolution Window Size:")
        conv_win_lbl.setStyleSheet("""
            QLabel {
                color: #FFFFFF !important;
                font-weight: bold !important;
                font-size: 12px !important;
                min-width: 150px !important;
            }
        """)
        conv_win_layout.addWidget(conv_win_lbl)
        self.conv_win_input = QLineEdit("10")
        self.conv_win_input.setMaximumWidth(100)
        conv_win_layout.addWidget(self.conv_win_input)
        hr_calc_layout.addLayout(conv_win_layout)
        hr_calc_layout.addSpacing(5)

        hr_calc_box.setLayout(hr_calc_layout)
        control_layout.addWidget(hr_calc_box)
        control_layout.addSpacing(10)

        # Preview settings
        prev_group = QGroupBox("Preview Settings")
        prev_layout = QVBoxLayout()

        psize_layout = QHBoxLayout()
        psize_label = QLabel("Preview Size (Seconds):")
        psize_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF !important;
                font-weight: bold !important;
                font-size: 12px !important;
                min-width: 150px !important;
            }
        """)
        psize_layout.addWidget(psize_label)
        self.psize_var = QLineEdit("1.0")
        self.psize_var.setMaximumWidth(100)
        psize_layout.addWidget(self.psize_var)
        prev_layout.addLayout(psize_layout)



        prev_group.setLayout(prev_layout)
        control_layout.addWidget(prev_group)

        # Buttons
        button_row = QHBoxLayout()
        analyze_btn = QPushButton("Run Analysis")
        analyze_btn.clicked.connect(self.run_beat_analysis)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #505050;
                border: none;
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """)
        
        stopButton = QPushButton("Cancel")
        stopButton.clicked.connect(self.abort_operation)
        stopButton.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                border: none;
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
        """)

        button_row.addWidget(analyze_btn)
        button_row.addWidget(stopButton)
        control_layout.addLayout(button_row)
        
        control_layout.addSpacing(20)

        control_layout.addStretch()
        control_frame.setLayout(control_layout)
        control_frame.setMaximumWidth(300)

        gp = QFrame()
        gp.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 2px solid #404040;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        graph_stack = QVBoxLayout()

        # ECG Preview
        self.ecg_display = pg.PlotWidget()
        self.ecg_display.setWindowTitle("ECG Preview")
        self.ecg_display.setLabel('left', 'Amplitude')
        self.ecg_display.setLabel('bottom', 'Time (s)')
        self.ecg_display.showGrid(x=True, y=True, alpha=0.3)
        self.ecg_display.addLegend()
        
        self.ecg_display.setBackground('#1A252F')
        self.ecg_display.getAxis('left').setTextPen('w')
        self.ecg_display.getAxis('bottom').setTextPen('w')
        self.ecg_display.getAxis('left').setPen('w')
        self.ecg_display.getAxis('bottom').setPen('w')

        # Heart Rate Preview
        self.bpm_chart = pg.PlotWidget()
        self.bpm_chart.setWindowTitle("Heart Rate Preview")
        self.bpm_chart.setLabel('left', 'BPM')
        self.bpm_chart.setLabel('bottom', 'Time (s)')
        self.bpm_chart.showGrid(x=True, y=True, alpha=0.3)
        self.bpm_chart.addLegend()
        
        self.bpm_chart.setBackground('#1A252F')
        self.bpm_chart.getAxis('left').setTextPen('w')
        self.bpm_chart.getAxis('bottom').setTextPen('w')
        self.bpm_chart.getAxis('left').setPen('w')
        self.bpm_chart.getAxis('bottom').setPen('w')

        graph_stack.addWidget(self.ecg_display)
        graph_stack.addWidget(self.bpm_chart)
        gp.setLayout(graph_stack)

        layout.addWidget(control_frame)
        layout.addWidget(gp)
        self.setLayout(layout)
        
        self.makePreviewPlot()

    def makePreviewPlot(self):
        if self.parent and self.parent.X_Data is not None and self.parent.Y_Data is not None:

            self.ecg_display.clear()
            self.ecg_display.plot(self.parent.X_Data, self.parent.Y_Data, 
                               pen=pg.mkPen(color=(0, 120, 255)), linewidth=2, label='ECG Signal')
            self.ecg_display.setTitle("ECG Preview - Uploaded Data")
            self.ecg_display.setLabel('bottom', "Time (s)")
            self.ecg_display.setLabel('left', "Amplitude")
            self.ecg_display.showGrid(x=True, y=True, alpha=0.3)
            self.ecg_display.addLegend()
            
            x_min, x_max = np.min(self.parent.X_Data), np.max(self.parent.X_Data)
            y_min, y_max = np.min(self.parent.Y_Data), np.max(self.parent.Y_Data)
            y_range = y_max - y_min
            margin = y_range * 0.1
            self.ecg_display.setXRange(x_min, x_max)
            self.ecg_display.setYRange(y_min - margin, y_max + margin)
            
            self.bpm_chart.clear()
            self.bpm_chart.setTitle("Heart Rate Preview")
            self.bpm_chart.setLabel('bottom', "Time (s)")
            self.bpm_chart.setLabel('left', "BPM")
            self.bpm_chart.showGrid(x=True, y=True, alpha=0.3)
            self.bpm_chart.addLegend()
            
        else:
            print("No ECG data")

    def run_beat_analysis(self):



        if self.parent and self.parent.data is not None:
            try:
                tw = float(self.window_input.text())
                tp = float(self.percentile_input.text())

                self.parent.processData = ECGProcessor(
                    self.parent.X_Data,
                    self.parent.Y_Data,
                    self.parent.fs
                )

                if hasattr(self.parent.processData, "render_analysis_results"):
                    self.parent.processData.render_analysis_results(
                        ecg_widget=self.ecg_display,
                        hr_widget=self.bpm_chart,
                        threshold_percentile=tp,
                        threshold_window=tw
                    )
                else:
                    ECGProcessor.render_analysis_results(
                        ecg_widget=self.ecg_display,
                        hr_widget=self.ecg_display,
                        threshold_percentile=tp,
                        threshold_window=tw
                    )
                
                if hasattr(self.parent.processData, 'HeartBeats') and self.parent.processData.HeartBeats is not None:
                    hb_count = np.sum(self.parent.processData.HeartBeats)
                    self.ecg_display.setTitle(f"ECG Preview: ({hb_count} beat detected)")
                    self.bpm_chart.setTitle(f"Heart Rate Preview")


            except ValueError as e:
                QMessageBox.warning(self, "input error", f"Please check value  {e}")
        else:
            QMessageBox.warning(self, "No data", "data is missing. Please upload data first.")

    def close_without_copying(self):
        # Close window box
        print("Closing window...")
        self.close()

    def transfer_and_exit(self):
        # mimicing copying the function to the main graph.

        if self.parent and self.parent.X_Data is not None and self.parent.Y_Data is not None:
            self.parent.main_graph.clear()
            
            for item in self.parent.main_graph.items():
                if isinstance(item, pg.LegendItem):
                    self.parent.main_graph.removeItem(item)
            
            self.parent.main_graph.plot(self.parent.X_Data, self.parent.Y_Data, pen=pg.mkPen(color=(0, 120, 255)), linewidth=2, label='ECG Signal')
            
            if hasattr(self.parent, 'processData') and self.parent.processData:
                if hasattr(self.parent.processData, 'HeartBeats') and self.parent.processData.HeartBeats is not None:
                    hb_mask = np.where(self.parent.processData.HeartBeats == 1)
                    if hb_mask[0].size > 0:
                        detected_beats_times = self.parent.X_Data[hb_mask]
                        detected_beats_values = self.parent.Y_Data[hb_mask]
                        
                        self.parent.main_graph.plot(detected_beats_times, detected_beats_values,
                                               pen=None, symbol='o', symbolSize=10, symbolBrush='r', 
                                               symbolPen=pg.mkPen(color='r', width=2), label='Detected Heart Beats')
                        
                        self.parent.main_graph.setTitle("ECG Signal with detected heart beats")
                    else:
                        self.parent.main_graph.setTitle("ECG Signal - no heart beats detected")
                else:
                    self.parent.main_graph.setTitle("ECG Signal")
            else:
                self.parent.main_graph.setTitle("ECG Signal")
            
            self.parent.main_graph.setLabel('bottom', "Time (s)")
            self.parent.main_graph.setLabel('left', "Amplitude")
            self.parent.main_graph.showGrid(x=True, y=True, alpha=0.3)
            self.parent.main_graph.addLegend()
            
            x_min, x_max = np.min(self.parent.X_Data), np.max(self.parent.X_Data)
            y_min, y_max = np.min(self.parent.Y_Data), np.max(self.parent.Y_Data)
            y_range = y_max - y_min
            margin = y_range * 0.1
            self.parent.main_graph.setXRange(x_min, x_max)
            self.parent.main_graph.setYRange(y_min - margin, y_max + margin)
            
        else:
            print("No ECG data")
        
        # Close the window
        self.close()

    def abort_operation(self):

        self.close()

    def cacr(self):
        if hasattr(self.parent, 'processData') and self.parent.processData:
            if hasattr(self.parent.processData, 'HeartBeats') and self.parent.processData.HeartBeats is not None:

                self.parent.update_main_plots()
                
            else:
                print("No analysis ")
        else:
            print("No analysis avail")
        
        # Close the window
        self.close()


class ECGApplication(QMainWindow):
    def __init__(self, csvPath=None):
        super().__init__()
        self.setWindowTitle("ECG Analysis")
        self.setGeometry(100, 100, 1200, 720)

        self.set_dark_theme()

        self.beat_markers = []
        self.th_lines = []
        self.X_Data = None
        self.Y_Data = None
        self.SamplingRate = None
        self.data = None
        self.fs = None

        self.SpliceLocations = []
        self.HeartBeats = None
        self.HeartBeats_Spliced = None
        self.Thresholds = None
        self.HeartRate_X = None
        self.HeartRate_Y = None
        self.Active_Version = 'raw'

        self.current_point = 0
        self.time_values = None
        self.ecg_values = None
        self.ecg_col = None
        self.selected_marker = None
        self.tooltip = None
        self.heart_line = None
        self.rect = None
        self.rect_start = None
        self.rect_end = None
        self.rects = []
        self._drawing = None
        self._dragging = None

        self.window_duration = 5
        self.view_start_index = 0
        
        self.view_locked = False


        self.setup_ui()
        self.setup_plots()
        self.setup_controls()




    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(38, 38, 38))
        palette.setColor(QPalette.ColorRole.Text, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        self.setPalette(palette)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        mL = QHBoxLayout(central)

        # Left: plots
        self.left_frame = QFrame()
        self.left_layout = QVBoxLayout(self.left_frame)

        # Right: controls
        self.right_frame = QFrame()
        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_frame.setMaximumWidth(360)

        mL.addWidget(self.left_frame, 2)
        mL.addWidget(self.right_frame, 1)

    def setup_plots(self):

        self.main_graph = pg.PlotWidget()
        self.main_graph.addLegend()
        self.main_graph.setTitle("ECG")
        self.main_graph.setLabel('left', "Amplitude")
        self.main_graph.setLabel('bottom', "Time (s)")
        self.left_layout.addWidget(self.main_graph)

        self.sc = pg.PlotWidget()
        self.sc.addLegend()
        self.sc.setTitle("Heart Rate")
        self.sc.setLabel('left', "BPM")
        self.sc.setLabel('bottom', "Time (s)")
        self.left_layout.addWidget(self.sc)

    def plot_uploaded_data_simple(self, x, y):
        print(f"Plotting {len(x)} point")
        
        self.main_graph.clear()
        
        self.main_graph.plot(x, y, pen='w', name="CSV Line")

        


    def setup_controls(self):
        heartbeat_group = QGroupBox("Heartbeats")
        hb_layout = QVBoxLayout(heartbeat_group)

        add_btn = QPushButton("Add Heartbeat (at cursor)")
        add_btn.clicked.connect(self.add_heartbeat)
        hb_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove Last Heartbeat")
        remove_btn.clicked.connect(self.remove_heartbeat)
        hb_layout.addWidget(remove_btn)

        self.right_layout.addWidget(heartbeat_group)

        removal_group = QGroupBox("Data Removal")
        removal_layout = QVBoxLayout(removal_group)
        toggle_btn = QPushButton("Toggle Removal Mode")
        toggle_btn.clicked.connect(self.toggle_removal_mode)
        removal_layout.addWidget(toggle_btn)
        draw_btn = QPushButton("Draw Removal Interval")
        draw_btn.clicked.connect(self.draw_removal_interval)
        removal_layout.addWidget(draw_btn)
        self.right_layout.addWidget(removal_group)

        view_group = QGroupBox("View")
        view_layout = QVBoxLayout(view_group)



        self.show_raw_checkbox = QCheckBox("Show Raw Signal")
        self.show_raw_checkbox.setChecked(True)
        view_layout.addWidget(self.show_raw_checkbox)

        self.show_partial_checkbox = QCheckBox("Show Partial Calculation Area")
        self.show_partial_checkbox.setChecked(True)
        view_layout.addWidget(self.show_partial_checkbox)

        upload_btn = QPushButton("Upload ECG Data")
        upload_btn.clicked.connect(self.load_csv_data)
        view_layout.addWidget(upload_btn)

        self.right_layout.addWidget(view_group)

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

        self.right_layout.addWidget(info_group)

        detection_group = QGroupBox("Beat Detection")
        detection_layout = QVBoxLayout(detection_group)
        detect_btn = QPushButton("Detect Beats")
        detect_btn.clicked.connect(self.launch_beat_detection)
        detection_layout.addWidget(detect_btn)
        
        show_original_btn = QPushButton("Show Original ECG")
        show_original_btn.clicked.connect(self.reset_to_original_data)
        detection_layout.addWidget(show_original_btn)
        
        self.right_layout.addWidget(detection_group)

        chart_group = QGroupBox("Chart Data")
        chart_layout = QVBoxLayout(chart_group)
        start_btn = QPushButton("Start")
        start_btn.clicked.connect(self.start_chart)
        chart_layout.addWidget(start_btn)
        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.stop_chart)
        chart_layout.addWidget(stop_btn)
        self.right_layout.addWidget(chart_group)

        self.coordinates_display = QLabel("(x, y) = (—, —)")
        self.coordinates_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.coordinates_display.setStyleSheet("background-color: #F0F0F0; color: #000000; padding: 5px; border-radius: 3px;")
        self.right_layout.addWidget(self.coordinates_display)

        self.right_layout.addStretch()


    def read_csv(self, filepath):
        try:
            file = pd.read_csv(filepath)

            if file.shape[1] < 2:
                raise ValueError("CSV must have at least 2 columns")
            
            x = file.iloc[:, 0].values
            y = file.iloc[:, 1].values
            

            
            x_nan = np.isnan(x).sum()
            y_nan = np.isnan(y).sum()

            
            self.X_Data, self.Y_Data = x, y
            self.SamplingRate = self.estimate_sampling_rate()
            
            return x, y
            
        except Exception as e:
            print(f"Error reading CSV. {e}")
            raise

    def estimate_sampling_rate(self):
        if self.X_Data is None or len(self.X_Data) < 2:
            return np.nan
        dt = np.diff(self.X_Data)
        dt = dt[np.isfinite(dt) & (dt > 0)]
        if dt.size == 0:
            return np.nan
        fs = 1.0 / np.mean(dt)
        self.fs = fs
        return fs

    def load_signal_data(self, what):
        try:
            df = pd.read_csv(what)
            column_names = df.columns
            print("Columns in the file:", df.columns)

            self.without_time = []

            # Assume the first column is the time column.
            self.signal_time = df[column_names[0]].values

            self.signal_data = {}

            for col in column_names:
                self.signal_data[col] = df[col].values

            for col in column_names:
                if col != "Time":
                    self.without_time.append(self.signal_data[col])

            self.signal_data["rest"] = np.transpose(np.array(self.without_time))
            print("Signal time:", self.signal_time)
            print("Rest data :", self.signal_data["rest"])

            print("Calling method")
            self.nothing()
        except Exception as e:
            print("Error loading", e)


    def nothing(self):
        data_dict = {"Time": self.signal_time}
        for key in self.signal_data:
            if key not in ["rest"]:
                if key != "Time":
                    data_dict[key] = self.signal_data[key]
        df = pd.DataFrame(data_dict)
        self.dographs(df)

    def dographs(self, df):
        
        print(f"Plotting {len(df)} rows")
        
        x = df['Time'].values
        y = df['Y'].values
        
        self.main_graph.clear()
        
        self.main_graph.plot(x, y, pen=pg.mkPen(color='g'), marker=pg.mkPen(color='r'))
        

    def update_plots(self, data: pd.DataFrame):
        if data is None or not isinstance(data, pd.DataFrame) or data.shape[1] < 2:
            self.main_graph.setTitle("ECG")
            self.sc.setTitle("Heart Rate")
            QMessageBox.warning(self, "no data", "no signal col to plot.")
            return

        time_col = data.columns[0]
        self.time_values = pd.to_numeric(data[time_col], errors='coerce').to_numpy()

        if not np.any(~np.isnan(self.time_values)):
            QMessageBox.warning(self, "time error", "time col contains no valid numbers.")
            return

        non_time_cols = list(data.columns[1:])

        self.main_graph.clear()
        self.sc.clear()
        if self.main_graph.legend():
            self.main_graph.removeItem(self.main_graph.legend())

        # Colors (rgb)
        colors = [
            (230, 25, 75),    # r
            (60, 180, 75),    # g
            (67, 99, 216),    # b
            (0, 191, 191),    # c
            (240, 50, 230),   # m
            (255, 225, 25),   # y
            (245, 130, 48),   # o
            (145, 30, 180),   # p
        ]

        first_valid_y = None

        for i, col in enumerate(non_time_cols):
            ecg_values = pd.to_numeric(data[col], errors='coerce').to_numpy()
            mask = ~np.isnan(self.time_values) & ~np.isnan(ecg_values)
            if not np.any(mask):
                continue
            pen = pg.mkPen(color=colors[i % len(colors)])
            self.main_graph.plot(self.time_values[mask], ecg_values[mask], pen=pen, linewidth=2.5, label=col)

            if first_valid_y is None:
                first_valid_y = ecg_values[mask]


        x_min, x_max = np.nanmin(self.time_values), np.nanmax(self.time_values)
        if np.isfinite(x_min) and np.isfinite(x_max) and x_max > x_min:
            start = x_min
            window_sec = 5
            if x_max - x_min > window_sec:
                self.main_graph.setXRange(x_min, x_min + window_sec)
            else:
                self.main_graph.setXRange(x_min, x_max)

        all_y = []
        for col in non_time_cols:
            ecg_values = pd.to_numeric(data[col], errors='coerce').to_numpy()
            all_y.append(ecg_values[~np.isnan(ecg_values)])
        if all_y:
            all_y = np.concatenate(all_y)
            y_min, y_max = float(np.nanmin(all_y)), float(np.nanmax(all_y))
            y_span = max(1e-9, y_max - y_min)
            margin = 0.1 * y_span
            self.main_graph.setYRange(y_min - margin, y_max + margin, auto=False)

        if first_valid_y is None:
            first_valid_y = np.array([0.0, 1.0])
        self._set_initial_ranges_and_lock(self.time_values, first_valid_y)

        self.data = data
        non_time_cols_filtered = [c for c in data.columns if c != time_col]
        if non_time_cols_filtered:
            self.ecg_col = non_time_cols_filtered[0]
            self.ecg_values = pd.to_numeric(data[self.ecg_col], errors='coerce').to_numpy()
        else:
            self.ecg_col = None
            self.ecg_values = None

        if self.current_point >= len(self.time_values):
            self.current_point = len(self.time_values) - 1
        if self.current_point < 0:
            self.current_point = 0

        xVal = self.time_values[self.current_point]
        if self.ecg_values is not None and np.isfinite(xVal):
            y_val = self.ecg_values[self.current_point]
            if not np.isfinite(y_val):
                finite_mask = np.isfinite(self.ecg_values)
                y_val = self.ecg_values[finite_mask][0] if np.any(finite_mask) else 0.0

            if self.selected_marker:
                self.main_graph.removeItem(self.selected_marker)
            self.selected_marker = self.main_graph.plot([xVal], [y_val], pen=pg.mkPen(color='r'), symbol='o', symbolSize=8)

            if self.tooltip:
                self.main_graph.removeItem(self.tooltip)
            self.tooltip = self.main_graph.addLabel(f'Time: {xVal:.3f}\nAmp: {y_val:.3f}', pos=(xVal, y_val))

            self.coordinates_display.setText(f"(x, y) = ({xVal:.3f}, {y_val:.3f})")

        self.main_graph.setTitle("ECG")
        self.sc.setTitle("Heart Rate")

    def _set_initial_ranges_and_lock(self, x_vals, y_vals):

        self._apply_view_lock(self.view_locked)



    def add_heartbeat(self):
        if self.ecg_values is not None and self.time_values is not None and len(self.time_values):
            x_val = self.time_values[self.current_point]
            y_val = self.ecg_values[self.current_point]
            marker = self.main_graph.plot([x_val], [y_val], pen=pg.mkPen(color='r'), symbol='o', symbolSize=10)
            self.beat_markers.append(marker)

    def remove_heartbeat(self):
        if self.beat_markers:
            marker = self.beat_markers.pop()
            self.main_graph.removeItem(marker)

    def toggle_removal_mode(self):
        pass

    def draw_removal_interval(self):
        pass

    def view_window(self):
        pass

    def ecg_y_limits(self):
        pass

    def hr_y_limits(self):
        pass

    def load_csv_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                df = pd.read_csv(file_path)
                x = df['Time'].values
                y = df['Y'].values
                
                self.data = df
                self.X_Data = x
                self.Y_Data = y
                
                self.SamplingRate = self.estimate_sampling_rate()
                self.fs = self.SamplingRate
                
                self.plot_uploaded_data_simple(x, y)
                
                if self.SamplingRate and np.isfinite(self.SamplingRate):
                    self.sampling_rate_label.setText(f"Sampling Rate (Hz): {self.SamplingRate:.1f}")
                
                if self.X_Data is not None and len(self.X_Data) > 1:
                    duration = self.X_Data[-1] - self.X_Data[0]
                    self.session_length_label.setText(f"Session Length (s): {duration:.1f}")
                
                self.filename_label.setText(f"Filename: {os.path.basename(file_path)}")
                self.filepath_label.setText(f"Filepath: {file_path}")
                

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed: {e}")
        else:
            print("No file selected")




    def launch_beat_detection(self):

        
        if self.data is None:
            QMessageBox.warning(self, "No Data", "Please upload data.")
            return
        
        if self.X_Data is None or self.Y_Data is None:
            QMessageBox.warning(self, "No Data", "ECG data missing. Plese upload data")
            return
            
        self.beat_window = BeatDetectionWindow(self)
        self.beat_window.show()

    def start_chart(self):
        pass

    def stop_chart(self):
        pass

    def reset_to_original_data(self):
        if self.X_Data is not None and self.Y_Data is not None:
            self.main_graph.clear()
            if self.main_graph.legend():
                self.main_graph.removeItem(self.main_graph.legend())
            
            self.main_graph.plot(self.X_Data, self.Y_Data, 
                               pen=pg.mkPen(color=(0, 120, 255)), linewidth=2, label='ECG Signal')
            self.main_graph.setTitle("ECG Signal")
            self.main_graph.setLabel('bottom', "Time (s)")
            self.main_graph.setLabel('left', "Amplitude")
            self.main_graph.showGrid(x=True, y=True, alpha=0.3)
            self.main_graph.addLegend()
            
            x_min, x_max = np.min(self.X_Data), np.max(self.X_Data)
            y_min, y_max = np.min(self.Y_Data), np.max(self.Y_Data)
            y_range = y_max - y_min
            margin = y_range * 0.1
            self.main_graph.setXRange(x_min, x_max)
            self.main_graph.setYRange(y_min - margin, y_max + margin)
            

    def update_main_plots(self):
        if hasattr(self, 'processData') and self.processData:
            self.main_graph.clear()
            if self.main_graph.legend():
                self.main_graph.removeItem(self.main_graph.legend())
            
            if getattr(self.processData, "HeartBeats", None) is not None:
                hb_mask = np.where(self.processData.HeartBeats == 1)
                if hb_mask[0].size:
                    detected_beats_times = self.X_Data[hb_mask]
                    detected_beats_values = self.Y_Data[hb_mask]
                    
                    self.main_graph.plot(self.X_Data, self.Y_Data, 
                                       pen=pg.mkPen(color=(0, 120, 255)), linewidth=2, label='ECG Signal')
                    self.main_graph.plot(detected_beats_times, detected_beats_values,
                                       pen=None, symbol='o', symbolSize=10, symbolBrush='r', 
                                       symbolPen=pg.mkPen(color='r', width=2), label='Detected Heart Beats')
                    self.main_graph.setTitle("ECG Signal with Detected Heart Beats")
                    
                    self.main_graph.setLabel('bottom', "Time (s)")
                    self.main_graph.setLabel('left', "Amplitude")
                    self.main_graph.showGrid(x=True, y=True, alpha=0.3)
                    self.main_graph.addLegend()
                    
                    y_min = np.min(self.Y_Data)
                    y_max = np.max(self.Y_Data)
                    y_range = y_max - y_min
                    margin = y_range * 0.1
                    self.main_graph.setYRange(y_min - margin, y_max + margin)
                else:
                    self.main_graph.plot(self.X_Data, self.Y_Data, 
                                       pen=pg.mkPen(color=(0, 120, 255)), linewidth=2, label='ECG Signal')
                    self.main_graph.setTitle("ECG Signal - No Heart Beats Detected")
                    self.main_graph.setLabel('bottom', "Time (s)")
                    self.main_graph.setLabel('left', "Amplitude")
                    self.main_graph.showGrid(x=True, y=True, alpha=0.3)
                    self.main_graph.addLegend()
            else:
                self.main_graph.plot(self.X_Data, self.Y_Data, 
                                   pen=pg.mkPen(color=(0, 120, 255)), linewidth=2, label='ECG Signal')
                self.main_graph.setTitle("ECG Signal - Heart Beat Detection Results")
                self.main_graph.setLabel('bottom', "Time (s)")
                self.main_graph.setLabel('left', "Amplitude")
                self.main_graph.showGrid(x=True, y=True, alpha=0.3)
                self.main_graph.addLegend()

            if getattr(self.processData, "HeartRate_X", None) is not None and getattr(self.processData, "HeartRate_Y", None) is not None:
                self.sc.clear()
                self.sc.setTitle("Heart Rate Data Available")
                self.sc.setLabel('bottom', "Time (s)")
                self.sc.setLabel('left', "BPM")
                self.sc.showGrid(x=True, y=True, alpha=0.3)

            self._apply_view_lock(self.view_locked)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.on_left()
        elif event.key() == Qt.Key.Key_Right:
            self.on_right()
        else:
            super().keyPressEvent(event)

    def on_left(self):
        if self.time_values is not None and self.current_point > 0:
            self.current_point -= 1
            self.update_selected_point()

    def on_right(self):
        if self.time_values is not None and self.current_point < len(self.time_values) - 1:
            self.current_point += 1
            self.update_selected_point()

    def update_selected_point(self):
        if self.time_values is not None and self.ecg_values is not None and len(self.time_values):
            idx = int(np.clip(self.current_point, 0, len(self.time_values) - 1))
            x_val = self.time_values[idx]
            y_val = self.ecg_values[idx]
            if not np.isfinite(y_val):
                finite_idx = np.where(np.isfinite(self.ecg_values))[0]
                if finite_idx.size:
                    nearest = finite_idx[np.argmin(np.abs(finite_idx - idx))]
                    y_val = self.ecg_values[nearest]
                else:
                    y_val = 0.0

            if self.selected_marker:
                self.main_graph.removeItem(self.selected_marker)
            self.selected_marker = self.main_graph.plot([x_val], [y_val], pen=pg.mkPen(color='r'), symbol='o', symbolSize=8)

            if self.tooltip:
                self.main_graph.removeItem(self.tooltip)
            self.tooltip = self.main_graph.addLabel(f'Time: {x_val:.3f}\nAmp: {y_val:.3f}', pos=(x_val, y_val))

            self.coordinates_display.setText(f"(x, y) = ({x_val:.3f}, {y_val:.3f})")

            self._apply_view_lock(self.view_locked)

    def _apply_view_lock(self, lock):
        pass

    def toggle_auto_range(self, checked):
        pass

if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else None

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    win = ECGApplication(csv_path)
    win.show()

    sys.exit(app.exec())


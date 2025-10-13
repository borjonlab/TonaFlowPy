import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QCheckBox, QFrame, QFileDialog, QMessageBox, QLineEdit, QGroupBox, 
    QHBoxLayout, QGridLayout,QToolBar, QMenuBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QAction
import pyqtgraph as pg


class BeatDetectionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Beat Detection Settings")
        self.setGeometry(100, 100, 1500, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.apply_styles()
        self.setup_ui()

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
        self.abs_check.setChecked(True)
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

        # Preview Settings Group
        prev_group = QGroupBox("Preview Settings")
        prev_layout = QVBoxLayout()

        psize_layout = QHBoxLayout()
        psize_label = QLabel("Preview Size (Seconds):")
        psize_label.setStyleSheet("min-width: 150px;")
        psize_layout.addWidget(psize_label)
        self.psize_input = QLineEdit("1.0")
        self.psize_input.setMaximumWidth(100)
        psize_layout.addWidget(self.psize_input)
        prev_layout.addLayout(psize_layout)

        prev_group.setLayout(prev_layout)
        control_layout.addWidget(prev_group)

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
        self.ecg_display.setBackground('#1A252F')

        # Heart Rate Preview plot
        self.hr_display = pg.PlotWidget()
        self.hr_display.setTitle("Heart Rate Preview")
        self.hr_display.setLabel('left', 'BPM')
        self.hr_display.setLabel('bottom', 'Time (s)')
        self.hr_display.showGrid(x=True, y=True, alpha=0.3)
        self.hr_display.setBackground('#1A252F')

        graph_layout.addWidget(self.ecg_display)
        graph_layout.addWidget(self.hr_display)
        graph_frame.setLayout(graph_layout)

        layout.addWidget(control_frame)
        layout.addWidget(graph_frame)
        self.setLayout(layout)

    def run_analysis(self):
        """Placeholder for analysis functionality"""
        QMessageBox.information(self, "Analysis", "Analysis functionality would be implemented here")


class ECGApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ECG Analysis Application")
        self.setGeometry(100, 100, 1800, 720)
        self.set_dark_theme()
        self.setup_ui()
        self.setup_menubar()

    def set_dark_theme(self):
        """Apply dark theme to the application"""
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
        self.main_graph = pg.PlotWidget()
        self.main_graph.setTitle("ECG Signal")
        self.main_graph.setLabel('left', "Amplitude")
        self.main_graph.setLabel('bottom', "Time (s)")
        self.main_graph.showGrid(x=True, y=True, alpha=0.3)
        plot_layout.addWidget(self.main_graph)

        # Heart rate plot
        self.hr_graph = pg.PlotWidget()
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

        control_layout.addStretch()
        main_layout.addWidget(control_frame, 1)

        
    def setup_menubar(self):
        menubar = self.menuBar()
        #File menu, new 
        file_menu = menubar.addMenu('File...')

        load_ecg_action = QAction("Load ECG File (.csv)", self)
        load_ecg_action.triggered.connect(self.load_csv_data)

        export_data_action = QAction("Export Data (.csv)",self)

        file_menu.addAction(load_ecg_action)
        file_menu.addAction(export_data_action)



        ecg_menu = menubar.addMenu('ECG...')
        filter_ecg_action = QAction("Filter ECG (CWT)", self)

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

        remove_btn = QPushButton("Remove Last Heartbeat")
        remove_btn.clicked.connect(self.remove_heartbeat)
        hb_layout.addWidget(remove_btn)

        layout.addWidget(heartbeat_group)

    def setup_removal_controls(self, layout):
        """Set up data removal control group"""
        removal_group = QGroupBox("Data Removal")
        removal_layout = QVBoxLayout(removal_group)
        
        toggle_btn = QPushButton("Toggle Removal Mode")
        toggle_btn.clicked.connect(self.toggle_removal_mode)
        removal_layout.addWidget(toggle_btn)
        
        draw_btn = QPushButton("Draw Removal Interval")
        draw_btn.clicked.connect(self.draw_removal_interval)
        removal_layout.addWidget(draw_btn)
        
        layout.addWidget(removal_group)

    def setup_view_controls(self, layout):
        """Set up view control group"""
        view_group = QGroupBox("View")
        view_layout = QVBoxLayout(view_group)

        self.show_raw_checkbox = QCheckBox("Show Raw Signal")
        self.show_raw_checkbox.setChecked(True)
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

    # def setup_detection_controls(self, layout):
    #     """Set up beat detection control group"""
    #     detection_group = QGroupBox("Beat Detection")
    #     detection_layout = QVBoxLayout(detection_group)
        
    #     detect_btn = QPushButton("Detect Beats")
    #     detect_btn.clicked.connect(self.launch_beat_detection)
    #     detection_layout.addWidget(detect_btn)
        
    #     show_original_btn = QPushButton("Show Original ECG")
    #     show_original_btn.clicked.connect(self.reset_to_original_data)
    #     detection_layout.addWidget(show_original_btn)
        
    #     layout.addWidget(detection_group)

    # def setup_chart_controls(self, layout):
    #     """Set up chart control group"""
    #     chart_group = QGroupBox("Chart Data")
    #     chart_layout = QVBoxLayout(chart_group)
        
    #     start_btn = QPushButton("Start")
    #     start_btn.clicked.connect(self.start_chart)
    #     chart_layout.addWidget(start_btn)
        
    #     stop_btn = QPushButton("Stop")
    #     stop_btn.clicked.connect(self.stop_chart)
    #     chart_layout.addWidget(stop_btn)
        
    #     layout.addWidget(chart_group)

    # Event handlers (placeholder implementations)
    def add_heartbeat(self):
        """Placeholder for add heartbeat functionality"""
        QMessageBox.information(self, "Add Heartbeat", "Add heartbeat functionality would be implemented here")

    def remove_heartbeat(self):
        """Placeholder for remove heartbeat functionality"""
        QMessageBox.information(self, "Remove Heartbeat", "Remove heartbeat functionality would be implemented here")

    def toggle_removal_mode(self):
        """Placeholder for toggle removal mode functionality"""
        QMessageBox.information(self, "Removal Mode", "Toggle removal mode functionality would be implemented here")

    def draw_removal_interval(self):
        """Placeholder for draw removal interval functionality"""
        QMessageBox.information(self, "Draw Interval", "Draw removal interval functionality would be implemented here")

    def load_csv_data(self):
        """Show file dialog for CSV selection"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            QMessageBox.information(self, "File Selected", f"Selected: {file_path}\nData loading would be implemented here")

    def launch_beat_detection(self):
        """Launch the beat detection window"""
        self.beat_window = BeatDetectionWindow(self)
        self.beat_window.show()

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
    
    window = ECGApplication()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
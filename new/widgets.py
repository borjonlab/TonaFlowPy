from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QCheckBox, QFrame, QFileDialog, QMessageBox, QLineEdit, QGroupBox, 
    QHBoxLayout, QGridLayout,QToolBar, QMenuBar
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt
import pyqtgraph as pg

import numpy as np

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
        self.threshold_line = pg.PlotDataItem()
        self.ecg_display.addItem(self.ECG_line)
        self.ecg_display.addItem(self.threshold_line)
        pass

    def connect_signals(self):
        # Connect inputs to emit signal whenever they change
        self.window_input.textChanged.connect(self.emit_settings)
        self.percentile_input.editingFinished.connect(self.emit_settings)
        self.abs_check.stateChanged.connect(self.emit_settings)
        self.conv_win_input.textChanged.connect(self.emit_settings)
        self.psize_input.textChanged.connect(self.emit_settings)
        



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



    def get_all_settings(self):
        settings = {
                "window": float(self.window_input.text()),
                "percentile": float(self.percentile_input.text()),
                "use_abs": self.abs_check.isChecked(),
                "conv_win": int(self.conv_win_input.text()),
                "preview_size": float(self.psize_input.text())
            }
        return settings
    

    def run_analysis(self):
        settings = self.get_all_settings()
        self.analysisRun.emit(settings)
    def close(self):
        self.hide()




class EcgPlot(pg.PlotWidget):
    def __init__(self):
        super().__init__()
        self.setup_plot_items()
        self.setup_mouse_events()

        self.RemovalRegions = []

    def setup_plot_items(self):
        self.ecg_line = pg.PlotDataItem(symbol='o',pen='g', symbolBrush='g', symbolSize = 4.5,width=1)
        self.heartbeats_line = pg.PlotDataItem(pen='r',symbolPen=None,symbol='o')
        self.point_selector = self.SelectedPoint(symbolPen = 'y', symbol = 'o')

        self.addItem(self.ecg_line)
        self.addItem(self.heartbeats_line)
        self.addItem(self.point_selector)

        # Set downsampling and cliptoview to true for performances
        self.ecg_line.setDownsampling(auto=True)
        self.ecg_line.setClipToView(True)
        self.heartbeats_line.setDownsampling(auto=True)
        self.heartbeats_line.setDownsampling(True)

    def setup_mouse_events(self):
        self.scene().sigMouseClicked.connect(self.mouse_clicked)

    # def insert_removal_region(self):
    #     region = pg.LinearRegionItem((4,5))
    #     self.addItem(region)
    #     self.RemovalRegions.append(region)

    # Event functions
    def mouse_clicked(self,evt):
        vb = self.plotItem.vb
        scene_coords = evt.scenePos()
        if self.sceneBoundingRect().contains(scene_coords) and evt.button() == Qt.MouseButton.LeftButton:
            mouse_point = vb.mapSceneToView(scene_coords)
            print(f'clicked plot X: {mouse_point.x()}, Y: {mouse_point.y()}, event: {evt}')
            

            # x_data, y_data = self.ecg_line.getData()
            x_data = self.ecg_line.xData
            y_data = self.ecg_line.yData
            nx = self.point_selector.try_selection(mouse_point.x(),mouse_point.y(),x_data, y_data)
            # x = [float(self.ecg_line.xData[nx])]
            # y = [float(self.ecg_line.yData[nx])]
            # self.selected_point.setData(x,y)
            # br = []
            # for i,x in enumerate(self.ecg_line.xData):
            #     br.append('g')
            #     if i == nx:
            #         br.append('r')
            # self.ecg_line.setSymbolBrush(br)
            
    class SelectedPoint(pg.PlotDataItem):
        def __init__(self, *args, **kargs):
            super().__init__(*args, **kargs)
            self.current_selection = None

        def get_nearest_point(self, x, y, queryX, queryY):
            queryX = np.asarray(queryX)
            queryY = np.asarray(queryY)

            if queryX.size == 0 or queryY.size == 0:
                return None

            dx = queryX - x
            dy = queryY - y
            dist_sq = dx**2 + dy**2
            dist_sq = np.sqrt(dist_sq)

            ix = np.argmin(dist_sq)
            return [float(queryX[ix])], [float(queryY[ix])], ix
            

        
        # in this function we will attempt to see if the X,Y coordinates (given by user input - ie mouseclick) 
        # are sufficiently close to a given point in the real data.
        def try_selection(self,x,y,queryX, queryY):
            closest_point = self.get_nearest_point(x,y,queryX,queryY)
            print(closest_point)
            
            self.setData(closest_point[0],closest_point[1])
            self.current_selection = (closest_point[0],closest_point[1],closest_point[2])

            
            # self.setData(x,y)

class HeartRatePlot(pg.PlotWidget):
    def __init__(self):
        super().__init__()
        self.setup_plot_items()
    def setup_plot_items(self):
        self.heart_rate_line = pg.PlotDataItem(pen='r')
        self.addItem(self.heart_rate_line)
            
            
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QCheckBox, QFrame, QFileDialog, QMessageBox, QLineEdit, QGroupBox,
    QHBoxLayout, QGridLayout, QToolBar, QMenuBar, QComboBox
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
import pyqtgraph as pg

import numpy as np


class RemovalRegion(pg.LinearRegionItem):
    b = pg.mkBrush(color=(0,0,255,125))
    removeRequest = pyqtSignal(object)
    def __init__(
        self,
        values=(0, 1),
        orientation='vertical',
        brush=b,
        pen=None,
        hoverBrush=None,
        hoverPen=None,
        movable=True,
        bounds=None,
        span=(0, 1),
        swapMode='sort',
        clipItem=None,
    ):
        super().__init__(
            values, orientation, brush, pen,
            hoverBrush, hoverPen, movable,
            bounds, span, swapMode, clipItem
        )
        

    def mouseDoubleClickEvent(self, ev):
        self.removeRequest.emit(self)
        ev.accept()



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
            "conv_win": int(self.conv_win_input.text()),
            "preview_size": float(self.psize_input.text())
        }
        return settings

    def run_analysis(self):
        settings = self.get_all_settings()
        self.analysisRun.emit(settings)

    def close(self):
        self.hide()




from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFrame,
    QPushButton, QLabel, QGroupBox, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
import pyqtgraph as pg


class FilteringWindow(QWidget):
    settingsChanged = pyqtSignal(dict)
    analysisRun = pyqtSignal(dict)
    def __init__(self, parent=None):
        super().__init__(parent)

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
        ## FFT Plot
        self.fft_line = pg.PlotDataItem()
        self.fft_lower_boundaries = pg.LinearRegionItem((0,float(self.cutlower.text())),movable=False)
        self.fft_upper_boundaries = pg.LinearRegionItem((float(self.cutUpper.text()),30000),movable=False)

        self.ecg_display.addItem(self.ECG_line)
        self.ecg_display.addItem(self.filtered_ecg_line)
        # self.filtered_ecg_display.addItem(self.filtered_ecg_line)
        self.fft_plot.addItem(self.fft_line)
        self.fft_plot.addItem(self.fft_lower_boundaries)
        self.fft_plot.addItem(self.fft_upper_boundaries)

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

        # self.filterType = QComboBox()
        # self.filterType.addItems(["Low-pass", "High-pass", "Band-pass", "Band-stop"])
        # filter_layout.addWidget(QLabel("Filter Type"))
        # filter_layout.addWidget(self.filterType)

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
        self.ecg_display.setBackground('#1A252F')
        leg = self.ecg_display.addLegend()
        
        # self.filtered_ecg_display = pg.PlotWidget(title="Filtered ECG")
        # self.filtered_ecg_display.setLabel('left', 'Amplitude')
        # self.filtered_ecg_display.setLabel('bottom', 'Time (s)')
        # self.filtered_ecg_display.showGrid(x=True, y=True, alpha=0.3)
        # self.filtered_ecg_display.setBackground('#1A252F')

        left_graph_layout.addWidget(self.ecg_display)
        # left_graph_layout.addWidget(self.filtered_ecg_display)

        # Right graph (third plot)
        self.fft_plot = pg.PlotWidget(title="FFT")
        self.fft_plot.setLabel('left', 'Power')
        self.fft_plot.setLabel('bottom', 'Frequency (Hz)')
        self.fft_plot.showGrid(x=True, y=True, alpha=0.3)
        self.fft_plot.setBackground('#1A252F')

        graph_layout.addLayout(left_graph_layout, stretch=2)
        graph_layout.addWidget(self.fft_plot, stretch=1)





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
                self.fft_plot.setData(ecg.fft_xf, ecg.fft_yy)

    def showEvent(self, event):
        super().showEvent(event)
        self.update_ecg_display()

    def close(self):
        self.hide()


class EcgPlot(pg.PlotWidget):
    def __init__(self):
        super().__init__()
        self.setup_plot_items()
        self.setup_mouse_events()
        self.setup_keyboard_events()
        self.setup_labels()
        self.setup_styling()

        self.RemovalRegions = []
    
    def setup_styling(self,style="dark"):
        if style == "light":
            self.getAxis('left').setPen(pg.mkPen(color='k', width=2))
            self.getAxis('left').setTextPen(pg.mkPen("#000000"))

            self.getAxis('bottom').setPen(pg.mkPen(color='k', width=2))
            self.getAxis('bottom').setTextPen(pg.mkPen("#000000"))
        else:
            self.getAxis('left').setPen(pg.mkPen(color='w', width=2))
            self.getAxis('left').setTextPen(pg.mkPen("#ffffff"))

            self.getAxis('bottom').setPen(pg.mkPen(color='w', width=2))
            self.getAxis('bottom').setTextPen(pg.mkPen("#ffffff"))
            

    def setup_labels(self):
        self.setLabel('left', 'ECG Value', units='mV or A.U.')
        

    def setup_plot_items(self):
        self.ecg_line = pg.PlotDataItem(symbol='o', pen='g', symbolBrush='g', symbolSize=2.5, width=1)
        self.filt_line = pg.PlotDataItem(symbol='o', pen='w', symbolBrush='w', symbolSize=2.5, width=1)
        self.heartbeats_line = pg.PlotDataItem(pen='r', symbolPen=None, symbol='o')
        self.point_selector = self.SelectedPoint(
            symbolPen='w',
            symbolBrush='w',
            symbol='o',
            symbolSize=15
        )
        self.coord_label = pg.TextItem(text='', color='w', anchor=(0.5, 1))
        self.coord_label.hide()
        self.point_selector.set_parent_plot(self)

        self.addItem(self.ecg_line)
        self.addItem(self.filt_line)
        self.addItem(self.heartbeats_line)
        self.addItem(self.point_selector)
        self.addItem(self.coord_label)

        # Set downsampling and cliptoview to true for performances
        self.ecg_line.setDownsampling(auto=True)
        self.ecg_line.setClipToView(True)
        self.filt_line.setDownsampling(auto=True)
        self.filt_line.setClipToView(True)
        self.heartbeats_line.setDownsampling(auto=True)
        self.heartbeats_line.setDownsampling(True)

    def setup_mouse_events(self):
        # self.scene().sigMouseClicked.connect(self.mouse_clicked)
        self.ecg_line.sigPointsClicked.connect(self.select)
        self.heartbeats_line.sigPointsClicked.connect(self.select)
        self.point_selector.sigPointsClicked.connect(self.select)
    def setup_keyboard_events(self):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    def keyPressEvent(self, event: QKeyEvent):
        view_box = self.getViewBox()
        if view_box is None:
            super().keyPressEvent(event)
            return
        x_range, y_range = view_box.viewRange()
        x_min, x_max = x_range
        visible_range = x_max - x_min
        shift_amount = visible_range * 0.1
        if event.key() == Qt.Key.Key_Left:
            xm = x_min - shift_amount
            newxm = x_max - shift_amount
            view_box.setXRange(xm, newxm, padding=0)
            event.accept()
        elif event.key() == Qt.Key.Key_Right:
            plusxmin = x_min + shift_amount
            plusxmax = x_max + shift_amount
            view_box.setXRange(plusxmin, plusxmax, padding=0)
            event.accept()
        else:
            super().keyPressEvent(event)

    def select(self, evt, pts):
        print(pts)
        if not hasattr(self.ecg_line, 'xData') or not hasattr(self.ecg_line, 'yData'):
            return
        if self.ecg_line.xData is None or self.ecg_line.yData is None:
            return
        if len(self.ecg_line.xData) == 0 or len(self.ecg_line.yData) == 0:
            return
        xp, yp = pts[0].pos()
        if self.point_selector.current_selection is not None:
            if xp == self.point_selector.current_selection[0]:
                self.point_selector.deselectPoint()
            else:
                self.point_selector.setPoint(self.ecg_line.xData, self.ecg_line.yData, xp, yp)
        elif self.point_selector.current_selection is None:
            self.point_selector.setPoint(self.ecg_line.xData, self.ecg_line.yData, xp, yp)
    class SelectedPoint(pg.PlotDataItem):
        def __init__(self, *args, **kargs):
            super().__init__(*args, **kargs)
            self.current_selection = None
            self.parent_plot = None

        def set_parent_plot(self, plot):
            self.parent_plot = plot

        def setPoint(self, XDT, Ydt, x, y):
            if XDT is None or Ydt is None or len(XDT) == 0 or len(Ydt) == 0:
                return
                
            # Get index 
            ixx = np.where(XDT == x)
            # ixy = np.where(Yd == y)
            self.current_selection = (x, y, ixx)
            self.setData([x], [y])
            
            if self.parent_plot and hasattr(self.parent_plot, 'coord_label'):
                xVal = f"{x:.4f}" if abs(x) < 10000 else f"{x:.3e}"
                yVal = f"{y:.4f}" if abs(y) < 10000 else f"{y:.3e}"
                text = f'X: {xVal}, Y: {yVal}'
                self.parent_plot.coord_label.setText(text)

                vb = self.parent_plot.getViewBox()
                if vb:
                    _, y_range = vb.viewRange()
                    y_min, y_max = y_range
                    visible_height = y_max - y_min
                    #adjusting 3 perc. of vis height above the point
                    y_offset = visible_height * 0.03
                    self.parent_plot.coord_label.setPos(x, y + y_offset)
                else:
                    self.parent_plot.coord_label.setPos(x, y)
                self.parent_plot.coord_label.setAnchor((0.5, 1))
                self.parent_plot.coord_label.show()
        def deselectPoint(self):
            self.current_selection = (None, None, None)
            self.setData([], [])
            if self.parent_plot and hasattr(self.parent_plot, 'coord_label'):
                self.parent_plot.coord_label.hide()


class HeartRatePlot(pg.PlotWidget):
    def __init__(self):
        super().__init__()
        self.setup_plot_items()
        self.setup_labels()
        self.setup_styling()

    def setup_styling(self,style="dark"):
        if style == "light":
            self.getAxis('left').setPen(pg.mkPen(color='k', width=2))
            self.getAxis('left').setTextPen(pg.mkPen("#000000"))

            self.getAxis('bottom').setPen(pg.mkPen(color='k', width=2))
            self.getAxis('bottom').setTextPen(pg.mkPen("#000000"))
        else:
            self.getAxis('left').setPen(pg.mkPen(color='w', width=2))
            self.getAxis('left').setTextPen(pg.mkPen("#ffffff"))

            self.getAxis('bottom').setPen(pg.mkPen(color='w', width=2))
            self.getAxis('bottom').setTextPen(pg.mkPen("#ffffff"))

    def setup_plot_items(self):
        self.heart_rate_line = pg.PlotDataItem(pen='r')
        self.addItem(self.heart_rate_line)
    
    def setup_labels(self):
        self.setLabel('left', 'Heart Rate', units='BPM')
        self.setLabel('bottom', 'Time', units='s')



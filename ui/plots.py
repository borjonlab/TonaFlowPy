from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent

import pyqtgraph as pg
import numpy as np

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
        self.heartbeats_line = pg.PlotDataItem(pen=None, symbolPen='r', symbolBrush='r', symbol='t')

        self.point_selector = self.SelectedPoint(
            symbolPen='w',
            symbolBrush='w',
            symbol='o',
            symbolSize=15
        )

        partial_brush = pg.mkBrush(color=(180,0,255,125))
        self.partial_calculation_region_beg = pg.LinearRegionItem(values=(0,0),orientation='vertical',brush=partial_brush,pen=pg.mkPen(color=(0,0,0,0)),movable=False)
        self.partial_calculation_region_end = pg.LinearRegionItem(values=(0,0),orientation='vertical',brush=partial_brush,pen=pg.mkPen(color=(0,0,0,0)),movable=False)

        self.coord_label = pg.TextItem(text='', color='w', anchor=(0.5, 1))
        self.coord_label.hide()
        self.point_selector.set_parent_plot(self)

        self.addItem(self.ecg_line)
        self.addItem(self.filt_line)
        self.addItem(self.heartbeats_line)
        self.addItem(self.point_selector)
        self.addItem(self.coord_label)
        self.addItem(self.partial_calculation_region_beg)
        self.addItem(self.partial_calculation_region_end)


        # Set downsampling and cliptoview to true for performances
        self.ecg_line.setDownsampling(auto=True)
        self.ecg_line.setClipToView(True)
        self.filt_line.setDownsampling(auto=True)
        self.filt_line.setClipToView(True)
        self.heartbeats_line.setDownsampling(auto=True)
        self.heartbeats_line.setDownsampling(True)

    def clear_plot(self):
        self.ecg_line.setData([], [])
        self.filt_line.setData([], [])
        self.heartbeats_line.setData([], [])
        self.point_selector.deselectPoint()
        self.coord_label.hide()
        for region in self.RemovalRegions:
            self.removeItem(region)
        self.RemovalRegions.clear()
        self.partial_calculation_region_beg.setRegion((0,0))
        self.partial_calculation_region_end.setRegion((0,0))

    def setup_mouse_events(self):
        # self.scene().sigMouseClicked.connect(self.mouse_clicked)
        self.ecg_line.sigPointsClicked.connect(self.select)
        self.filt_line.sigPointsClicked.connect(self.select)
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

        # Is the signal filtered? If so, we use the filt_line. If not, use ecg_line
        if self.filt_line.xData is not None:
            line = self.filt_line
        else:
            line = self.ecg_line
        if self.point_selector.current_selection is not None:
            if xp == self.point_selector.current_selection[0]:
                self.point_selector.deselectPoint()
            else:
                self.point_selector.setPoint(line.xData, line.yData, xp, yp)
        elif self.point_selector.current_selection is None:
            self.point_selector.setPoint(line.xData, line.yData, xp, yp)

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
        partial_pen = pg.mkPen(color=(180,0,255,125),width=8)
        self.partial_calculation_heart_rate_beg = pg.PlotDataItem(pen = partial_pen,symbolPen = None,symbol=None,width=3)
        self.partial_calculation_heart_rate_end = pg.PlotDataItem(pen = partial_pen,symbolPen = None,symbol=None,width=3)
        self.addItem(self.heart_rate_line)
        self.addItem(self.partial_calculation_heart_rate_beg)
        self.addItem(self.partial_calculation_heart_rate_end)

    def clear_plot(self):
        self.heart_rate_line.setData([], [])
        self.partial_calculation_heart_rate_beg.setData([], [])
        self.partial_calculation_heart_rate_end.setData([], [])
    
    def setup_labels(self):
        self.setLabel('left', 'Heart Rate', units='BPM')
        self.setLabel('bottom', 'Time', units='s')


####################################### Plot Widgets #######################################
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
        

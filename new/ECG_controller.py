from ecg import ECG

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from View import ECGApplication

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from widgets import BeatDetectionWindow
import pyqtgraph as pg

class ECG_controller(QObject):
    # Signals
    dataLoaded = pyqtSignal(int)

    def __init__(self,parent_widget: "ECGApplication"):
        super().__init__()
        self.ecg:ECG # Don't initialize it until the user loads data
        self.parent: "ECGApplication" = parent_widget
        self.setup_events()
        self.removal_regions = {"object":[]}
        pass
    
    def setup_events(self):
        self.dataLoaded.connect(self.update_ecg_plot)

    def load_data(self):
        self.ecg = ECG() # User loaded data - initialize the ECG. This way when a user loads another file, the ECG class and its properties become a clean slate. 
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Open CSV", "", "CSV Files (*.csv)")
        success = self.ecg.read_csv(file_path)
        self.dataLoaded.emit(success)

    def update_ecg_plot(self):
        self.parent.main_graph.ecg_line.setData(self.ecg.X_Data, self.ecg.Y_Data)
        if self.ecg.HeartBeats is not None:
            self.parent.main_graph.heartbeats_line.setData(self.ecg.X_Data[self.ecg.HeartBeats==1],self.ecg.Y_Data[self.ecg.HeartBeats==1])
            self.ecg.calculate_heart_rate()
            self.update_heartrate_plot()

    def update_heartrate_plot(self):
        if self.removal_regions is not None:
            # self.ecg.splice_ECG(self.removal_regions["region"])
            self.ecg.splice_ECG(self.get_removal_regions())
        self.parent.hr_graph.heart_rate_line.setData(self.ecg.HeartRate_X, self.ecg.HeartRate_Y)

    def add_heartbeat(self):
        # Get the current selection for the plot
        selected_point = self.parent.main_graph.point_selector.current_selection
        if selected_point is None:
            QMessageBox.information(self.parent, "No point selected!", "Please select a point.")
        elif self.ecg.HeartBeats is None:
            QMessageBox.information(self.parent, "No beat detection!", "Beat detection not run.")
        else:
            self.ecg.HeartBeats[selected_point[2]] = 1
            self.update_ecg_plot()
            # deselect point
            self.parent.main_graph.point_selector.deselectPoint()
            

    def remove_heartbeat(self):
        selected_point = self.parent.main_graph.point_selector.current_selection
        if selected_point is None:
            QMessageBox.information(self.parent, "No point selected!", "Please select a point.")
        elif self.ecg.HeartBeats is None:
            QMessageBox.information(self.parent, "No beat detection!", "Beat detection not run.")
        else:
            self.ecg.HeartBeats[selected_point[2]] = 0
            self.update_ecg_plot()
            self.parent.main_graph.point_selector.deselectPoint()
            
    


    def get_removal_regions(self):
        reg = []
        for r in self.removal_regions['object']:
            reg.append(r.getRegion())
        return reg


    def insert_removal_region(self):
        # self.parent.main_graph.insert_removal_region()
        # Insert a removal region
        region = pg.LinearRegionItem((4,5))
        region.sigRegionChanged.connect(self.update_ecg_plot)
        self.parent.main_graph.addItem(region)
        

        reg = region.getRegion()
        self.removal_regions["object"].append(region)
        # self.removal_regions["region"].append(reg)
        # self.ecg.splice_ECG([reg[0],reg[1]])
        # self.ecg.SpliceLocations.append([reg[0],reg[1]])
        self.ecg.calculate_heart_rate()
        self.update_ecg_plot()






    ##### Beat detection window 
    def open_beat_detection(self):
        self.beatwindow = BeatDetectionWindow(self.parent)

        # connect signals
        self.beatwindow.settingsChanged.connect(self.run_BD_preview)
        self.beatwindow.analysisRun.connect(self.run_BD)

        self.beatwindow.emit_settings()
        self.beatwindow.show()


    def run_BD(self,settings):
        self.ecg.detect_heart_beats(threshold_percentile=settings["percentile"],
                                    threshold_window=settings["window"]
                                    )
        self.beatwindow.close()
        self.update_ecg_plot()

    def run_BD_preview(self, settings: dict):
        self.ecg.detect_heart_beats(threshold_percentile=settings["percentile"],
                                    threshold_window=settings["window"]
                                    )
        self.plot_BD_preview()
            

    def plot_BD_preview(self):
        self.beatwindow.ECG_line.setData(self.ecg.X_Data, self.ecg.Y_Data)
        self.beatwindow.threshold_line.setData(self.ecg.Thresholds_X, self.ecg.Thresholds)

    


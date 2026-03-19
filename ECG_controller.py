from ECG import ECG

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from View import ECGApplication

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
import numpy as np

from widgets import BeatDetectionWindow, FilteringWindow, RemovalRegion
import pyqtgraph as pg
from PyQt6.QtCore import Qt
import scipy


class ECG_controller(QObject):
    # Signals
    dataLoaded = pyqtSignal(int)

    def __init__(self, parent_widget: "ECGApplication"):
        super().__init__()
        self.ecg: ECG
        self.parent: "ECGApplication" = parent_widget
        self.setup_events()
        self.removal_regions = {"object": []}
        pass



    def setup_events(self):
        self.dataLoaded.connect(self.update_ecg_plot)

    def load_data(self):
        self.ecg = ECG()  # User loaded data - initialize the ECG. This way when a user loads another file, the ECG class and its properties become a clean slate.
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Open CSV", "", "CSV Files (*.csv)")
        success = self.ecg.read_csv(file_path)
        self.dataLoaded.emit(success)

    def update_ecg_plot(self, success=1, *args):
        if not success:
            return
        if self.ecg.X_Data() is not None and self.ecg.Y_Data() is not None:
            if len(self.ecg.X_Data()) > 0 and len(self.ecg.Y_Data()) > 0:
                if self.ecg.Is_Filtered == True:
                    # ECG is filtered, so display the filtered line along with the raw data. We will also need to edit the line of the ecg_line so that the alpha is lowered. 
                    self.parent.main_graph.filt_line.setData(self.ecg.X_Data(), self.ecg.Y_Data())
                    self.parent.main_graph.ecg_line.setAlpha(.1,False)
                self.parent.main_graph.ecg_line.setData(self.ecg.X_Data(request_raw=True),self.ecg.Y_Data(request_raw=True))
                view_box = self.parent.main_graph.getViewBox()
                # if view_box:
                #     view_box.autoRange()

        if self.ecg.HeartBeats is not None:
            self.parent.main_graph.heartbeats_line.setData(self.ecg.X_Data()[self.ecg.HeartBeats == 1],
                                                           self.ecg.Y_Data()[self.ecg.HeartBeats == 1])
            self.ecg.calculate_heart_rate()
            self.update_heartrate_plot()

    def update_heartrate_plot(self):
        if self.removal_regions is not None:
            # self.ecg.splice_ECG(self.removal_regions["region"])
            self.ecg.splice_ECG(self.get_removal_regions())
            self.ecg.calculate_heart_rate()
        self.parent.hr_graph.heart_rate_line.setData(self.ecg.HeartRate_X, self.ecg.HeartRate_Y)

    def add_heartbeat(self):
        # Get the current selection for the plot
        selected_point = self.parent.main_graph.point_selector.current_selection
        if selected_point[
            0] is None:  # subscript with 0, because technically a tuple of None is NOT None, so it selects all the points which is insane
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
        if selected_point[0] is None:
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
        if self.ecg.HeartBeats is not None:
            # Get the current view of the screen, that is where we will insert 
            xrange = self.parent.main_graph.getViewBox().viewRange()[0]
            b = (xrange[0] + xrange[1]) / 2
            u = b + xrange[1]/10
            region = RemovalRegion((b,u))
            region.sigRegionChanged.connect(self.update_ecg_plot)
            region.removeRequest.connect(self.remove_removal_region)
            self.parent.main_graph.addItem(region)

            reg = region.getRegion()
            self.removal_regions["object"].append(region)
            # self.removal_regions["region"].append(reg)
            # self.ecg.splice_ECG([reg[0],reg[1]])
            # self.ecg.SpliceLocations.append([reg[0],reg[1]])
            self.ecg.calculate_heart_rate()
            self.update_ecg_plot()
        else:
            QMessageBox.critical(self.parent,"Beat Detection Not Run!", "Beat detection has not been run. Removal Regions cannot be inserted.")

    def show_raw_checked(self):
        checkstatus = self.parent.show_raw_checkbox.checkState()
        if checkstatus == Qt.CheckState.Checked:
            self.parent.main_graph.ecg_line.setAlpha(1,False)
            self.parent.main_graph.filt_line.setAlpha(.2,False)
        else:
            self.parent.main_graph.ecg_line.setAlpha(.2,False)
            self.parent.main_graph.filt_line.setAlpha(1,False)


    def remove_removal_region(self, region: RemovalRegion):
        # Remove from plot
        self.parent.main_graph.removeItem(region)

        # Remove from list
        if region in self.removal_regions["object"]:
            self.removal_regions["object"].remove(region)

        # Update ECG plot
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

    def run_BD(self, settings):
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
        self.beatwindow.ECG_line.setData(self.ecg.X_Data(), self.ecg.Y_Data())
        self.beatwindow.threshold_line.setData(self.ecg.Thresholds_X, self.ecg.Thresholds)




    ##### Filtering 
    def open_filter_ecg(self):
        self.filterwindow = FilteringWindow(self.parent)
        self.filterwindow.show()

        self.filterwindow.analysisRun.connect(self.run_filter)

        self.filterwindow.settingsChanged.connect(self.plot_ecg_filt_preview)
        self.filterwindow.run_analysis
        self.plot_filt_preview()
        self.plot_fft_preview()
        self.plot_ecg_filt_preview({'low_cutoff':1,'high_cutoff':self.ecg.SamplingRate/2 -1})
        # Set the textboxes to default values
        self.filterwindow.cutlower.setText("1")
        self.filterwindow.cutUpper.setText(str(int(self.ecg.SamplingRate/2 -1)))

    def plot_filt_preview(self):
        self.filterwindow.ECG_line.setData(self.ecg.X_Data(), self.ecg.Y_Data())

    def plot_fft_preview(self):
        self.ecg.calculate_fft()
        self.filterwindow.fft_line.setData(self.ecg.fft_xf,self.ecg.fft_yy)
        #calculate y lim range, we will do everything from 0.023 on because there is a large spike @ 0 
        up = np.max(self.ecg.fft_yy[3:])
        lo = np.min(self.ecg.fft_yy[3:])
        self.filterwindow.fft_plot.setYRange(lo,up)
        self.filterwindow.fft_plot.setXRange(np.min(self.ecg.fft_xf),np.max(self.ecg.fft_xf))
        # Update the lines for the filter boundaries in the FFT Plot 
        


    def run_filter(self, settings: dict):
        self.ecg.wavelet_bandpass(lowcutoff=settings['low_cutoff'], highcutoff=settings['high_cutoff'],set = True) #Add set = true to set the filtered data to the object
        self.filterwindow.close()
        self.update_ecg_plot()

    def plot_ecg_filt_preview(self, settings: dict):
        filtecg = self.ecg.wavelet_bandpass(lowcutoff=settings['low_cutoff'], highcutoff=settings['high_cutoff'])
        self.filterwindow.fft_lower_boundaries.setRegion((0,settings['low_cutoff']))
        self.filterwindow.fft_upper_boundaries.setRegion((settings['high_cutoff'],self.ecg.SamplingRate/2 -1))
        self.filterwindow.filtered_ecg_line.setData(self.ecg.X_Data(),filtecg)

    # def calculate_fft(self):
    #     xdata = self.ecg.X_Data()
    #     ydata = self.ecg.Y_Data()
    #     N = len(xdata)
    #     T = 1/self.ecg.SamplingRate
    #     yf = scipy.fftpack.fft(ydata)
    #     xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    #     yy = 2.0/N * np.abs(yf[:N//2])

        # self.filterwindow.fft_line.setData(xf,yy)

        # fig, ax = plt.subplots()
        # ax.plot(xf, 2.0/N * np.abs(yf[:N//2]))
        # plt.show()


    ##### Exporting 

    def export_csv(self):

        if not hasattr(self, 'ecg') or self.ecg is None:
            QMessageBox.warning(self.parent, "N/a Data", "No ECG uploaded.")
            return
        
        if self.ecg.X_Data() is None or self.ecg.Y_Data() is None:
            QMessageBox.warning(self.parent, "N/a Data", "No ECG uploaded")
            return
        
        if len(self.ecg.X_Data()) == 0 or len(self.ecg.Y_Data()) == 0:
            QMessageBox.warning(self.parent, "N/a Data", "No ECG uploaded")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self.parent, "Export CSV", "", "CSV Files (*.csv)")
        
        if file_path:
            try:
                df = pd.DataFrame({
                    'Time': self.ecg.X_Data(),
                    'Amplitude': self.ecg.Y_Data(),
                    'HeartBeats': self.ecg.HeartBeats,
                    'HeartRate': self.ecg.HeartRate_Y
                })
                
                # Exporting
                df.to_csv(file_path, index=False)
                QMessageBox.information(self.parent, "CSV exported", f"exported @ {file_path}")
            except Exception as e:
                QMessageBox.critical(self.parent, "CSV export failed", f"Failed  {str(e)}")





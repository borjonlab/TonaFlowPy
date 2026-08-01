from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QFileDialog, QMessageBox

import pyqtgraph as pg
import pandas as pd
import numpy as np

from core.ECG import ECG
from ui.windows.filtering import FilteringWindow
from ui.windows.beat_detection import BeatDetectionWindow
from ui.plots import RemovalRegion
from ui.windows.about import AboutWindow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.View import TonaFlow




class ECG_controller(QObject):
    # Signals
    dataLoaded = pyqtSignal(int)

    def __init__(self, parent_widget: "TonaFlow"):
        super().__init__()
        self.ecg: ECG
        self.parent: "TonaFlow" = parent_widget
        self.setup_events()
        self.removal_regions = {"object": []}
        pass



    def setup_events(self):
        self.dataLoaded.connect(self.update_ecg_plot)
        self.dataLoaded.connect(self.enable_buttons)

    def load_data(self):
        self.ecg = ECG()  # User loaded data - initialize the ECG. This way when a user loads another file, the ECG class and its properties become a clean slate.
        file_path, _ = QFileDialog.getOpenFileName(self.parent, "Open CSV", "", "CSV Files (*.csv)")
        success = self.ecg.read_csv(file_path)
        if success != 0:
            self.dataLoaded.emit(success)
        else:
            QMessageBox.critical(self.parent,"ERROR: Data not readable!","Couldn't read the file. Please upload a CSV with exactly two columns: time in column 1 and ECG signal in column 2!")

    def update_ecg_plot(self, success=1, *args):
        if not success:
            return
        if self.ecg.HeartBeats is not None:
            self.parent.ECG_Axis.heartbeats_line.setData(self.ecg.X_Data()[self.ecg.HeartBeats == 1],
                                                           self.ecg.Y_Data()[self.ecg.HeartBeats == 1])
            self.ecg.calculate_heart_rate()
            self.update_heartrate_plot()
        if self.ecg.X_Data() is not None and self.ecg.Y_Data() is not None:
            if len(self.ecg.X_Data()) > 0 and len(self.ecg.Y_Data()) > 0:
                if self.ecg.Is_Filtered == True:
                    # ECG is filtered, so display the filtered line along with the raw data. We will also need to edit the line of the ecg_line so that the alpha is lowered. 
                    self.parent.ECG_Axis.filt_line.setData(self.ecg.X_Data(), self.ecg.Y_Data())
                    self.parent.ECG_Axis.ecg_line.setAlpha(.1,False)
                self.parent.ECG_Axis.ecg_line.setData(self.ecg.X_Data(request_raw=True),self.ecg.Y_Data(request_raw=True))
                view_box = self.parent.ECG_Axis.getViewBox()


                if self.ecg.HeartBeats is not None:
                    # plot the partial calculation window, first get the convolution window size
                    winlen = self.ecg.det_settings['conv_win']
                    partialrange = winlen/2
                    self.parent.ECG_Axis.partial_calculation_region_beg.setRegion((0,partialrange))
                    # Get length of data
                    mx = np.max(self.ecg.X_Data())
                    self.parent.ECG_Axis.partial_calculation_region_end.setRegion((mx-partialrange,mx))
                    
                    # Now do it for the heart rate data, first we need to get heart rate X and Y from 0:partialrange
                    begix = np.abs(self.ecg.X_Data() - partialrange).argmin()
                    begx = self.ecg.X_Data()[0:begix]
                    begy = self.ecg.HeartRate_Y[0:begix]
                    self.parent.HR_Axis.partial_calculation_heart_rate_beg.setData(begx,begy)

                    endx_start = np.max(self.ecg.X_Data()) - partialrange
                    end_start_ix = np.abs(self.ecg.X_Data() - endx_start).argmin()
                    end_stop_ix = len(self.ecg.X_Data())

                    endx = self.ecg.X_Data()[end_start_ix:end_stop_ix]
                    endy = self.ecg.HeartRate_Y[end_start_ix:end_stop_ix]
                    self.parent.HR_Axis.partial_calculation_heart_rate_end.setData(endx,endy)

    def enable_buttons(self):
        self.parent.add_heartbeat_button.setEnabled(True)
        self.parent.remove_heartbeat_button.setEnabled(True)
        self.parent.show_filtered_signal_toggle.setEnabled(True)
        self.parent.show_partial_calc_toggle.setEnabled(True)
        self.parent.show_removed_heartbeats_toggle.setEnabled(True)
        self.parent.insert_removal_region_button.setEnabled(True)


    def update_heartrate_plot(self):
        if self.removal_regions is not None:
            # self.ecg.splice_ECG(self.removal_regions["region"])
            self.ecg.splice_ECG(self.get_removal_regions())
            self.ecg.calculate_heart_rate()
        self.parent.HR_Axis.heart_rate_line.setData(self.ecg.HeartRate_X, self.ecg.HeartRate_Y)

    def add_heartbeat(self):
        # Get the current selection for the plot
        selected_point = self.parent.ECG_Axis.point_selector.current_selection
        if self.ecg.HeartBeats is None:
            QMessageBox.information(self.parent, "No beat detection!", "Beat detection not run.")
            self.parent.ECG_Axis.point_selector.deselectPoint()
        elif selected_point[0] is None:  # subscript with 0, because technically a tuple of None is NOT None, so it selects all the points which is insane
            QMessageBox.information(self.parent, "No point selected!", "Please select a point.")
        else:
            self.ecg.HeartBeats[selected_point[2]] = 1
            self.update_ecg_plot()
            # deselect point
            self.parent.ECG_Axis.point_selector.deselectPoint()

    def remove_heartbeat(self):
        selected_point = self.parent.ECG_Axis.point_selector.current_selection
        if selected_point[0] is None:
            QMessageBox.information(self.parent, "No point selected!", "Please select a point.")
        elif self.ecg.HeartBeats is None:
            QMessageBox.information(self.parent, "No beat detection!", "Beat detection not run.")
        else:
            self.ecg.HeartBeats[selected_point[2]] = 0
            self.update_ecg_plot()
            self.parent.ECG_Axis.point_selector.deselectPoint()

    def get_removal_regions(self):
        reg = []
        for r in self.removal_regions['object']:
            reg.append(r.getRegion())
        return reg

    def insert_removal_region(self):
        if self.ecg.HeartBeats is not None:
            # Get the current view of the screen, that is where we will insert 
            xrange = self.parent.ECG_Axis.getViewBox().viewRange()[0]
            b = (xrange[0] + xrange[1]) / 2
            u = b + xrange[1]/10
            region = RemovalRegion((b,u))
            region.sigRegionChanged.connect(self.update_ecg_plot)
            region.removeRequest.connect(self.remove_removal_region)
            self.parent.ECG_Axis.addItem(region)

            reg = region.getRegion()
            self.removal_regions["object"].append(region)
            # self.removal_regions["region"].append(reg)
            # self.ecg.splice_ECG([reg[0],reg[1]])
            # self.ecg.SpliceLocations.append([reg[0],reg[1]])
            self.ecg.calculate_heart_rate()
            self.update_ecg_plot()
        else:
            QMessageBox.critical(self.parent,"Beat Detection Not Run!", "Beat detection has not been run. Removal Regions cannot be inserted.")

    def show_filtered_signal_toggled(self):
        togglestatus = self.parent.show_filtered_signal_toggle.isChecked()
        if togglestatus == 1:
            self.parent.ECG_Axis.ecg_line.setAlpha(1,False)
        else:
            self.parent.ECG_Axis.ecg_line.setAlpha(.05,False)

    def show_partial_calc_toggled(self):
        togglestatus = self.parent.show_partial_calc_toggle.isChecked()

        if togglestatus == 1:
            self.parent.HR_Axis.partial_calculation_heart_rate_beg.setVisible(True)
            self.parent.HR_Axis.partial_calculation_heart_rate_end.setVisible(True)
            self.parent.ECG_Axis.partial_calculation_region_beg.setVisible(True)
            self.parent.ECG_Axis.partial_calculation_region_end.setVisible(True)
        else:
            self.parent.HR_Axis.partial_calculation_heart_rate_beg.setVisible(False)
            self.parent.HR_Axis.partial_calculation_heart_rate_end.setVisible(False)
            self.parent.ECG_Axis.partial_calculation_region_beg.setVisible(False)
            self.parent.ECG_Axis.partial_calculation_region_end.setVisible(False)
        # Force redraw
        self.parent.ECG_Axis.repaint()


    def remove_removal_region(self, region: RemovalRegion):
        # Remove from plot
        self.parent.ECG_Axis.removeItem(region)

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
        self.ecg.det_settings = self.beatwindow.get_all_settings()
        self.beatwindow.show()

    def run_BD(self, settings):
        self.ecg.detect_heart_beats(threshold_percentile=settings["percentile"],
                                    threshold_window=settings["window"]
                                    )
        self.beatwindow.close()
        self.update_ecg_plot()

    def run_BD_preview(self, settings: dict):
        self.ecg.detect_heart_beats(threshold_percentile=settings["percentile"],
                                    threshold_window=settings["window"],
                                    use_abs=settings["use_abs"]
                                    )
        self.plot_BD_preview()

    def plot_BD_preview(self):
        settings = self.beatwindow.get_all_settings()
        if settings["use_abs"] == True:
            self.beatwindow.ECG_line.setData(self.ecg.X_Data(),np.abs(self.ecg.Y_Data()))
        else:
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
        self.plot_ecg_filt_preview({'low_cutoff':1,'high_cutoff':self.ecg.SamplingRate/2 -1})
        # Set the textboxes to default values
        self.filterwindow.cutlower.setText("1")
        self.filterwindow.cutUpper.setText(str(int(self.ecg.SamplingRate/2 -1)))

    def plot_filt_preview(self):
        self.filterwindow.ECG_line.setData(self.ecg.X_Data(), self.ecg.Y_Data())


    def run_filter(self, settings: dict):
        self.ecg.wavelet_bandpass(lowcutoff=settings['low_cutoff'], highcutoff=settings['high_cutoff'],set = True) #Add set = true to set the filtered data to the object
        self.filterwindow.close()
        self.update_ecg_plot()

    def plot_ecg_filt_preview(self, settings: dict):
        filtecg = self.ecg.wavelet_bandpass(lowcutoff=settings['low_cutoff'], highcutoff=settings['high_cutoff'])
        self.filterwindow.filtered_ecg_line.setData(self.ecg.X_Data(),filtecg)



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

    def open_about_window(self):
        self.win = AboutWindow(self.parent)
        self.win.show()
        self.win.center_on_parent()

    def open_settings_window(self):
        pass



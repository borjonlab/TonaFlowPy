import numpy as np
import pandas as pd
import argparse
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QFrame, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont
import pyqtgraph as pg
from scipy.signal.windows import gaussian as gausswin
from scipy.signal import butter, lfilter
from scipy.fft import fft, fftfreq
import sys


class ECGProcessor:
    def __init__(self, X_Data, Y_Data, SamplingRate):
        self.X_Data = X_Data
        self.Y_Data = Y_Data
        self.SamplingRate = SamplingRate
        self.HeartBeats = None
        self.HeartBeats_Spliced = None
        self.SpliceLocations = []
        self.Active_Version = 'raw'
        self.Thresholds = None
        self.Thresholds_X = None
        self.HeartRate_Y = None
        self.HeartRate_X = None

    def render_analysis_results(self, ecg_widget=None, hr_widget=None, threshold_percentile=95.0, threshold_window=5.0):
        # Detect heart beats first
        self.find_heartbeats(
            merge_window=50,
            threshold_percentile=threshold_percentile,
            threshold_window=threshold_window
        )
        
        # self.splice_ECG(test=True, approximate_locations=[[0, 10000], [40000, 220000]])
        
        self.calculate_heart_rate()

        x = self.X_Data
        y = self.Y_Data
        
        if ecg_widget is not None:
            ecg_widget.clear()
            ecg_widget.plot(x, y, pen=pg.mkPen(color=(0, 120, 255)), linewidth=2, label="ECG")
            
            if self.HeartBeats is not None:
                xb = x[np.where(self.HeartBeats == 1)[0]]
                yb = y[np.where(self.HeartBeats == 1)[0]]
                if len(xb) > 0:
                    ecg_widget.plot(xb.to_numpy(), yb.to_numpy(), pen=None, symbol='o', symbolSize=8, 
                                   symbolBrush='r', symbolPen=None, label="Detected Beats")
            
            if self.Thresholds_X is not None and self.Thresholds is not None:
                ecg_widget.plot(self.Thresholds_X, self.Thresholds, 
                               pen=pg.mkPen(color='r', style=pg.QtCore.Qt.PenStyle.DashLine), 
                               label="Thresholds")
            
            for loc in self.SpliceLocations:
                x1 = loc[0] / self.SamplingRate
                x2 = loc[1] / self.SamplingRate
                w = x2 - x1
                h = np.max(y)
                rect = pg.QtWidgets.QGraphicsRectItem(x1, np.min(y), w, h - np.min(y))
                rect.setOpacity(0.3)
                rect.setBrush(pg.mkBrush('y'))
                ecg_widget.addItem(rect)
            
            ecg_widget.setTitle("ECG Signal with Detected Heartbeats")
            ecg_widget.setLabel('bottom', "Time (s)")
            ecg_widget.setLabel('left', "Amplitude")
            ecg_widget.showGrid(x=True, y=True, alpha=0.3)
            ecg_widget.addLegend()

        if hr_widget is not None:
            hr_widget.setTitle("Heart Rate Preview")

    def find_heartbeats(self, method='dynamicThreshold', threshold_percentile=None, threshold_window=None,
                           merge_window=20):
        if method == 'dynamicThreshold':
            t = self.X_Data
            y = self.Y_Data
            fs = self.SamplingRate

            ses_len = t[len(t) - 1] - t[0]
            ses_size = len(t)

            rows = int(np.floor(ses_len / threshold_window))
            cols = int(fs * threshold_window)
            Time = np.zeros((rows, cols))
            for g in range(0, int(np.floor(ses_len / threshold_window)) + 1):
                det = [i for i in range(int(1 + threshold_window * (g - 1) * fs), int(threshold_window * g * fs) + 1)]
                Time[g - 1, :] = det

            Time = np.int64(Time)
            spks = []
            thresholds = np.zeros((rows, cols))
            for g in range(0, Time.shape[0]):
                seg = y[Time[g, :]]
                p = np.percentile(seg, threshold_percentile)
                spks.append(Time[g][np.where(seg > p)] / fs)
                thresholds[g, :] = p

            spks = np.hstack(spks)
            mSpks = np.copy(spks)
            mSpks = np.sort(mSpks)

            thresholds = np.reshape(thresholds, thresholds.shape[0] * thresholds.shape[1])

            ix = [i for i in range(0, t.shape[0])]
            reftable = np.transpose(np.array([ix, t, y]))

            nspk = []
            nspk2 = []
            for ix in range(0, mSpks.shape[0]):
                this = reftable[reftable[:, 1] == mSpks[ix], :][0]
                winix = np.array([i for i in range(np.int64(this[0] - (merge_window / 2)), np.int64(this[0] + (merge_window / 2)))])
                window = reftable[winix[winix > 0], :]
                m = np.max(window[:, 2])
                i = np.argmax(window[:, 2])
                nspk.append(window[i, 1])
                nspk2.append(window[i, 0])

            nspk2 = np.int64(nspk2)
            dum = np.zeros(int(np.ceil(ses_len * fs)))
            dum[nspk2] = 1
            self.HeartBeats = np.copy(dum)
            self.Thresholds = thresholds
            self.Thresholds_X = np.arange(0, thresholds.shape[0] / fs, 1 / fs)

    def process_ecg_signal(self, method='cwt'):
        if method == 'cwt':
            pass

    def cut_ecg_segments(self, approximate_locations, test=False):
        temp_ecg = np.copy(self.Y_Data)
        temp_heartbeats = np.copy(self.HeartBeats)

        if test == True:
            for loc in approximate_locations:
                L = loc[0]
                R = loc[1]

                if L <= 0:
                    left_beat_index = 0
                for i in range(L, 0, -1):
                    if self.HeartBeats[i] == 1:
                        left_beat_index = i
                        break
                    elif i == 0:
                        left_beat_index = -1

                if R >= len(self.HeartBeats) - 1:
                    right_beat_index = len(self.HeartBeats)
                for i in range(R, len(self.HeartBeats) - 1, 1):
                    if self.HeartBeats[i] == 1:
                        right_beat_index = i
                        break
                    elif i == len(self.HeartBeats) - 1:
                        right_beat_index = -1

                temp_heartbeats[left_beat_index:right_beat_index] = np.nan
                self.SpliceLocations.append([left_beat_index, right_beat_index])
                self.Active_Version = 'spliced'
                self.HeartBeats_Spliced = temp_heartbeats

    def calculate_heart_rate(self, window_size=10):
        if self.Active_Version == 'spliced':
            hb = np.copy(self.HeartBeats_Spliced)
            ix = np.where(np.isnan(hb))
            hb = np.delete(hb, ix)
            fs = self.SamplingRate
            gauss_filter = gausswin(fs * window_size, std=1 * fs)
            gauss_filter = gauss_filter / np.sum(gauss_filter)
            self.HeartRate_Y = np.convolve(hb, gauss_filter, 'same') * fs * 60
            for loc in self.SpliceLocations:
                nanpad = np.empty(loc[1] - loc[0])
                nanpad[:] = np.nan
                self.HeartRate_Y = np.insert(self.HeartRate_Y, loc[0], nanpad)
            self.HeartRate_X = np.arange(0, self.HeartRate_Y.shape[0] / fs, 1 / fs)
        else:
            fs = self.SamplingRate
            gauss_filter = gausswin(fs * window_size, std=1 * fs)
            gauss_filter = gauss_filter / np.sum(gauss_filter)
            self.HeartRate_Y = np.convolve(self.HeartBeats, gauss_filter, 'same') * fs * 60
            self.HeartRate_X = np.arange(0, self.HeartRate_Y.shape[0] / fs, 1 / fs)

    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        nyq = 0.5 * self.SamplingRate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        y = lfilter(b, a, self.Y_Data)
        return y

    def get_components(self):
        if self.Active_Version == 'raw':
            return self.X_Data
        elif self.Active_Version == 'filtered':
            return self.X_Data_Filtered


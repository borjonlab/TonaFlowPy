import numpy as np
import pandas as pd

from scipy.signal.windows import gaussian as gausswin
from scipy.signal import butter, lfilter

from ssqueezepy import cwt, wavelets, Wavelet, icwt
from ssqueezepy.wavelets import center_frequency
from ssqueezepy.utils import make_scales


class ECG:
    def __init__(self):
        ## Raw Data
        self.X_Data_Raw = []
        self.Y_Data_Raw = []

        self.X_Data_Filtered = []
        self.Y_Data_Filtered = []

        # self.X_Data() = []
        # self.Y_Data() = []

        self.SamplingRate = None
        ## inits
        self.X_Data_Filtered, self.Y_Data_Filtered = None, None
        self.SpliceLocations = []
        self.HeartBeats = None
        self.HeartBeats_Spliced = None
        self.Thresholds = None
        # Heart Rate
        self.HeartRate_X = None
        self.HeartRate_Y = None
        ## Active versioning
        self.Active_Version = 'raw'
        # Filtering
        self.Is_Filtered = False
        
        # FFT 
        self.fft_xf = None
        self.fft_yy = None

        # Detection settings
        self.det_settings = None

    # Setup Functions
    def estimate_sampling_rate(self):
        return 1 / np.mean(np.diff(self.X_Data()))

    def read_csv(self, filepath):
        try:
            file = pd.read_csv(filepath)
            x = file.iloc[:, 0].to_numpy(dtype='float')
            y = file.iloc[:, 1].to_numpy(dtype='float')
            
            # Normalize so that baseline is around zero 
            y = y - np.mean(y)
            # return x,y

            self.X_Data_Raw = x
            self.Y_Data_Raw = y
            self.SamplingRate = self.estimate_sampling_rate()
            return 1
        except:
            return 0

    # Get Functions
    def X_Data(self,request_raw = False):
        # request_raw is for whether we are specifically requesting the RAW signal. 
        # Are we specifically requesting the raw data? 
        if request_raw == True:
            return self.X_Data_Raw
        
        # Check if it is filtered 
        if self.Is_Filtered:
            return self.X_Data_Filtered
        else:
            return self.X_Data_Raw
    def Y_Data(self,request_raw = False):
        # request_raw is for whether we are specifically requesting the RAW signal. 
        if request_raw == True:
            return self.Y_Data_Raw
        
        # Check whether it is filtered
        if self.Is_Filtered:
            return self.Y_Data_Filtered
        else:
            return self.Y_Data_Raw


    # Hard Calculations
    def calculate_heart_rate(self, window_size=10):
        fs = self.SamplingRate
        gauss_filter = gausswin(int(fs * window_size), std=1 * fs)
        gauss_filter = gauss_filter / np.sum(gauss_filter)

        if self.Active_Version == 'spliced':
            hb = np.copy(self.HeartBeats_Spliced)
            valid = ~np.isnan(hb)
            hb_clean = hb[valid]

            hr_clean = np.convolve(hb_clean, gauss_filter, 'same') * fs * 60

            # Rebuild with NaNs
            self.HeartRate_Y = np.full_like(hb, np.nan, dtype=float)
            self.HeartRate_Y[valid] = hr_clean
            self.HeartRate_X = np.arange(0, len(hb) / fs, 1 / fs)

        else:
            hb = self.HeartBeats
            self.HeartRate_Y = np.convolve(hb, gauss_filter, 'same') * fs * 60
            self.HeartRate_X = np.arange(0, len(hb) / fs, 1 / fs)





    def detect_heart_beats(self, method='dynamicThreshold', threshold_percentile=97.5, threshold_window=1,
                           merge_window=20, use_abs = False):
        if method == 'dynamicThreshold':
            t = self.X_Data()
            y = self.Y_Data()
            fs = self.SamplingRate

            if use_abs:
                y = np.abs(y)

            ses_len = t[len(t) - 1] - t[0]  # length of session
            ses_size = len(t)  # Size of session in elements

            # Segment into N second windows; whatever user suggests.
            # Default to 1
            rows = int(np.floor(ses_len / threshold_window))
            cols = int(fs * threshold_window)
            Time = np.zeros((rows, cols))
            for g in range(0, int(np.floor(ses_len / threshold_window)) + 1):
                det = [i for i in range(int(1 + threshold_window * (g - 1) * fs), int(threshold_window * g * fs) + 1)]
                Time[g - 1, :] = det

            # Cast time to int64
            Time = np.int64(Time)
            spks = []
            thresholds = np.zeros((rows, cols))  # To save the thresholds
            for g in range(0, Time.shape[0]):
                seg = y[Time[g, :]]
                p = np.percentile(seg,
                                  threshold_percentile)  # This is the value that becomes the threshold for segment `g`
                spks.append(Time[g][np.where(seg > p)] / fs)
                # Append to the thresholds
                thresholds[g, :] = p
            # unstack the peaks, because it is nested
            spks = np.hstack(spks)
            mSpks = np.copy(spks)  # Make a copy of the array.. bc python name refs lol
            mSpks = np.sort(mSpks)

            # reshape the thresholds
            thresholds = np.reshape(thresholds, thresholds.shape[0] * thresholds.shape[1])

            # Now, we look at every single peak, and then find the max and minimum
            # within a given window.
            # Create a reference table, with [index, t, y]
            ix = [i for i in range(0, t.shape[0])]
            reftable = np.transpose(np.array([ix, t, y]))

            # Window size in elements
            nspk = []
            nspk2 = []
            for ix in range(0, mSpks.shape[0]):
                this = reftable[reftable[:, 1] == mSpks[ix], :][0]
                winix = np.array([i for i in range(np.int64(this[0] - (merge_window / 2)),
                                                   np.int64(this[0] + (merge_window / 2)))])

                window = reftable[winix[winix > 0], :]
                m = np.max(window[:, 2])
                i = np.argmax(window[:, 2])
                # nspk.append()
                nspk.append(window[i, 1])
                nspk2.append(window[i, 0])
            # Cast npsk2 to int64
            nspk2 = np.int64(nspk2)
            # Create a dummy array for the heart beats
            # dum = np.zeros(int(np.ceil(ses_len*fs)))
            dum = np.zeros(len(self.X_Data()))

            dum[nspk2] = 1  # Set heartbeats = 1
            # Assign to self.beats
            self.HeartBeats = np.copy(dum)
            self.Thresholds = thresholds
            self.Thresholds_X = np.arange(0, thresholds.shape[0] / fs, 1 / fs)

    def filter_ECG(self, method='cwt'):
        if method == 'cwt':
            pass

    def splice_ECG(self, approximate_locations, test=False):
        # Reset splices each time
        self.SpliceLocations = []
        temp_heartbeats = np.copy(self.HeartBeats)

        for loc in approximate_locations:
            L = np.argmin(np.abs(self.X_Data() - loc[0]))
            R = np.argmin(np.abs(self.X_Data() - loc[1]))

            # Find first beat to the left
            left_beat_index = next((i for i in range(L, 0, -1) if self.HeartBeats[i] == 1), 0)
            # Find first beat to the right
            right_beat_index = next((i for i in range(R, len(self.HeartBeats)) if self.HeartBeats[i] == 1),
                                    len(self.HeartBeats) - 1)

            temp_heartbeats[left_beat_index:right_beat_index] = np.nan
            self.SpliceLocations.append([left_beat_index, right_beat_index])

        self.Active_Version = 'spliced'
        self.HeartBeats_Spliced = temp_heartbeats

        # Find the first heartbeat to the left
        # left_segment = np.where(e.HeartBeats[:L] == 1)
        # left_beat = left_segment[0][-1]
        # # Find the first heartbeat to the right
        # right_segment = np.where(e.HeartBeats[R:]==1)
        # right_beat = right_segment[0][0]
        # right_segment = np.where(e.HeartBeats[])
        # right_beat = right_segment[0][0] # Just the first el
        # temp_ecg[splicelocations] = np.nan # nan out the splice locations

    ## Other
    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        nyq = 0.5 * self.SamplingRate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        y = lfilter(b, a, self.Y_Data())
        return y
        # return b, a

    # def wavelet_bandpass(self):
    #     from ssqueezepy import cwt
    #     from ssqueezepy.experimental import scale_to_freq
    #     wavelet = ('morlet', {'mu': 10})
    #     N2 = 1024
    #     y2 = self.Y_Data()
    #     sc = 80
    #     Wx2, scales2, *_ = cwt(y2, wavelet, fs=N2, scales='log')
    #     freq2 = scale_to_freq(scales2, wavelet, N2, fs=N2 / sc)
    #     power2 = (abs(Wx2)) ** 2
    #     pass

    def wavelet_bandpass(self,lowcutoff,highcutoff,set=False):
        

        N = len(self.Y_Data())
        fs = self.SamplingRate

        wavelet = Wavelet('morlet')
        # print("changed")
        # Calculate cutoffs in scales 
        
        highcut_scale = (center_frequency(wavelet) * fs) / highcutoff
        lowcut_scale = (center_frequency(wavelet) * fs) / lowcutoff

        scales_filtered = make_scales(N, scaletype='log', nv=32, min_scale = highcut_scale, max_scale = lowcut_scale)
        
        # Calculate
        Wx, _ = cwt(self.Y_Data(request_raw=True), wavelet, scales = scales_filtered)
        YRec = icwt(Wx, wavelet, scales_filtered)

        if set == True:
            self.X_Data_Filtered = self.X_Data()
            self.Y_Data_Filtered = YRec
            # Set Is Filtered to true
            self.Is_Filtered = True
        else:
            return YRec

    
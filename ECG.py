import scipy
import numpy as np
import pandas as pd
import argparse
from matplotlib import pyplot as plt
from matplotlib import patches
from scipy.signal.windows import gaussian as gausswin
from scipy.signal import butter, lfilter
from scipy.fft import fft, fftfreq


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
                           merge_window=20):
        if method == 'dynamicThreshold':
            ###### TEMPORARY DECS
            # t = self.active_ecg.X_Data
            # y = self.active_ecg.Y_Data
            # fs = self.active_ecg.Fs
            t = self.X_Data()
            y = self.Y_Data()
            fs = self.SamplingRate

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
        from ssqueezepy import cwt, wavelets, Wavelet, icwt
        from ssqueezepy.wavelets import center_frequency
        from ssqueezepy.utils import make_scales, cwt_scalebounds
        import matplotlib.pyplot as plt

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


        # plt.figure()
        # plt.plot(YRec)
        # plt.plot(self.Y_Data())
        # plt.show()

    def calculate_fft(self):
        xdata = self.X_Data()
        ydata = self.Y_Data()
        N = len(xdata)
        T = 1/self.SamplingRate
        yf = scipy.fftpack.fft(ydata)
        xf = np.linspace(0.0,1.0/(2.0*T),N//2)
        yy = 2.0/N * np.abs(yf[:N//2])

        self.fft_xf = xf
        self.fft_yy = yy
        
        return (xf,yy)

    #     xdata = self.ecg.X_Data
    #     ydata = self.ecg.Y_Data
    #     N = len(xdata)
    #     T = 1/self.ecg.SamplingRate
    #     yf = scipy.fftpack.fft(ydata)
    #     xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    #     yy = 2.0/N * np.abs(yf[:N//2])

    # Get and Set functions
    # def get_components(self):
    #     if self.Active_Version == 'raw':
    #         return self.X_Data()
    #     elif self.Active_Version == 'filtered':
    #         return self.X_Data_Filtered

# # Debug and testing

# e = ECG("ex.csv")
# e.detect_heart_beats(merge_window=50,threshold_percentile=99)
# approx_locations =[[0,10000],[40000,220000]]
# e.splice_ECG(test = True,approximate_locations=approx_locations)
# e.calculate_heart_rate()


# xb = e.X_Data[np.where(e.HeartBeats == 1)]
# yb = e.Y_Data[np.where(e.HeartBeats == 1)]
# x = e.X_Data
# y = e.Y_Data
# xthr = e.Thresholds_X
# ythr = e.Thresholds

# yFilt = e.butter_bandpass(2,30,1000)


# f = plt.figure()
# ax1 = plt.subplot(2,1,1)
# plt.plot(xb,yb,marker='.',markersize=8,markerfacecolor='red',linestyle='None')
# plt.plot(x,y)
# plt.plot(xthr,ythr,linestyle='--',color='red')
# plt.grid(True)
# plt.legend(["Heartbeats","ECG","Thresholds","Removed Data"])

# for loc in e.SpliceLocations:
#     x1 = loc[0] / e.SamplingRate
#     x2 = loc[1] / e. SamplingRate
#     w = x2-x1
#     h = np.max(e.Y_Data)
#     r = patches.Rectangle((x1,np.min(e.Y_Data)),w,h - np.min(e.Y_Data),alpha=.5)
#     ax1.add_patch(r)
# # patches.Rectangle((e.SpliceLocations[0][0],e.SpliceLocations[0][1]),5,5)


# plt.subplot(2,1,2, sharex= ax1)
# plt.plot(e.HeartRate_X,e.HeartRate_Y)
# plt.grid(True)
# plt.show()

# f2 = plt.figure()
# for i in np.arange(1,4,1):
#     yf = e.butter_bandpass(i,499,1000)
#     plt.plot(yf,alpha = 0.5)
# plt.legend([f"lo={i}Hz" for i in np.arange(1,10,2)])
# plt.show()


import numpy as np
import pandas as pd 
import argparse
from matplotlib import pyplot as plt
from scipy.signal.windows import gaussian as gausswin
from scipy.signal import butter, lfilter
from scipy.fft import fft,fftfreq

class ECG:
    def __init__(self,csvPath):
        self.X_Data, self.Y_Data = self.read_csv(csvPath)
        self.read_csv(csvPath)
        self.SamplingRate = self.estimate_sampling_rate()    
        ## inits
        self.X_Data_Filtered, self.Y_Data_Filtered = None, None
        self.SpliceLocations = None
        self.HeartBeats = None
        self.Thresholds = None
        # Heart Rate
        self.HeartRate_X = None
        self.HeartRate_Y = None
        ## Active versioning
        self.Active_Version = 'raw'



    # Setup Functions 
    def estimate_sampling_rate(self):
        return 1/np.mean(np.diff(self.X_Data))
    
    def read_csv(self,filepath):
        file = pd.read_csv(filepath)
        x = file.iloc[:,0].to_numpy()
        y = file.iloc[:,1].to_numpy()
        return x,y
    
    # Hard Calculations 

    def calculate_heart_rate(self,window_size = 10, smoothing_factor = 0.7):
        fs = self.SamplingRate
        # Add something here to take care of the spliced version
        gauss_filter = gausswin(fs*window_size, std=1*fs) #stdev of 1sec (1*fs)
        gauss_filter = gauss_filter / np.sum(gauss_filter)
        # Convolve the gaussian window over the binary array of heartbeats
        self.HeartRate_Y = np.convolve(self.HeartBeats,gauss_filter,'same') * fs * 60
        self.HeartRate_X = np.arange(0,self.HeartRate_Y.shape[0]/fs,1/fs)
        
                
    def detect_heart_beats(self,method='dynamicThreshold',threshold_percentile = 97.5, threshold_window = 1, merge_window = 20):
        if method == 'dynamicThreshold':
            ###### TEMPORARY DECS            
            # t = self.active_ecg.X_Data
            # y = self.active_ecg.Y_Data
            # fs = self.active_ecg.Fs
            t = self.X_Data
            y = self.Y_Data
            fs = self.SamplingRate



            ses_len = t[len(t)-1] - t[0] # length of session
            ses_size = len(t) # Size of session in elements

            # Segment into N second windows; whatever user suggests. 
            # Default to 1
            rows = int(np.floor(ses_len/threshold_window))
            cols = int(fs*threshold_window)
            Time = np.zeros((rows,cols))
            for g in range(0,int(np.floor(ses_len/threshold_window))+1):
                det = [i for i in range(int(1+threshold_window*(g-1)*fs),int(threshold_window*g*fs)+1)]
                Time[g-1,:] = det
            
            # Cast time to int64
            Time = np.int64(Time)
            spks = []
            thresholds = np.zeros((rows,cols)) # To save the thresholds
            for g in range(0,Time.shape[0]):
                seg = y[Time[g,:]]
                p = np.percentile(seg,threshold_percentile) # This is the value that becomes the threshold for segment `g`
                spks.append(Time[g][np.where(seg>p)]/fs)
                # Append to the thresholds
                thresholds[g,:] = p
            # unstack the peaks, because it is nested
            spks = np.hstack(spks)
            mSpks = np.copy(spks) # Make a copy of the array.. bc python name refs lol
            mSpks = np.sort(mSpks)

            # reshape the thresholds
            thresholds = np.reshape(thresholds,thresholds.shape[0]*thresholds.shape[1])
            

            # Now, we look at every single peak, and then find the max and minimum 
            # within a given window. 
            # Create a reference table, with [index, t, y]
            ix = [i for i in range(0,t.shape[0])]
            reftable = np.transpose(np.array([ix,t,y]))

            # Window size in elements
            nspk = []
            nspk2 = []
            for ix in range(0,mSpks.shape[0]):
                this = reftable[reftable[:,1] == mSpks[ix],:][0]
                winix = np.array([i for i in range(np.int64(this[0] - (merge_window/2)),
                                            np.int64(this[0] + (merge_window/2)))])
                
                window = reftable[winix[winix>0],:]
                m = np.max(window[:,2])
                i = np.argmax(window[:,2])
                # nspk.append()
                nspk.append(window[i,1])
                nspk2.append(window[i,0])
            # Cast npsk2 to int64
            nspk2 = np.int64(nspk2)
            # Create a dummy array for the heart beats
            dum = np.zeros(int(np.ceil(ses_len*fs)))
            dum[nspk2] = 1 # Set heartbeats = 1
            # Assign to self.beats
            self.HeartBeats = np.copy(dum)
            self.Thresholds = thresholds
            self.Thresholds_X = np.arange(0, thresholds.shape[0]/fs, 1/fs)
    
    def filter_ECG(self,method='cwt'):
        if method == 'cwt':
            pass

    def splice_ECG(self, test=False):
        splicelocations = self.SpliceLocations
        temp_ecg = np.copy(self.Y_Data)
        if test == True:
            splicelocations = np.array(([15000, 20000],)) # Place the comma there so that `for in` treats each as a row, regardless of it's length
            for loc in splicelocations:
                L = loc[0]
                R = loc[1]
                # Find the first heartbeat to the left
                left_segment = np.where(e.HeartBeats[:15000] == 1)
                left_beat = left_segment[0][-1]
                # Find the first heartbeat to the right
                # right_segment = np.where(e.HeartBeats[])
                # right_beat = right_segment[0][0] # Just the first el
                # temp_ecg[splicelocations] = np.nan # nan out the splice locations

    
    ## Other
    def butter_bandpass(self,lowcut, highcut, fs, order=5):
        nyq = 0.5 * self.SamplingRate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        y = lfilter(b,a,self.Y_Data)
        return y
        # return b, a


    # Get and Set functions 
    def get_components(self):
        if self.Active_Version == 'raw':
            return self.X_Data
        elif self.Active_Version == 'filtered':
            return self.X_Data_Filtered




    


# Debug and testing 

e = ECG("ex.csv")
e.detect_heart_beats(merge_window=50,threshold_percentile=99)
e.calculate_heart_rate()

xb = e.X_Data[np.where(e.HeartBeats == 1)]
yb = e.Y_Data[np.where(e.HeartBeats == 1)]
x = e.X_Data
y = e.Y_Data
xthr = e.Thresholds_X
ythr = e.Thresholds

yFilt = e.butter_bandpass(2,30,1000)


f = plt.figure()
ax1 = plt.subplot(2,1,1)
plt.plot(xb,yb,marker='.',markersize=8,markerfacecolor='red',linestyle='None')
plt.plot(x,y)
plt.plot(xthr,ythr,linestyle='--',color='red')
plt.grid(True)
plt.legend(["Heartbeats","ECG","Thresholds"])

plt.subplot(2,1,2, sharex= ax1)
plt.plot(e.HeartRate_X,e.HeartRate_Y)
plt.grid(True)
plt.show()

f2 = plt.figure()
for i in np.arange(1,4,1):
    yf = e.butter_bandpass(i,499,1000)
    plt.plot(yf,alpha = 0.5)
plt.legend([f"lo={i}Hz" for i in np.arange(1,10,2)])
plt.show()

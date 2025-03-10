import numpy as np
import pandas as pd 
import argparse

class ECG:
    def __init__(self,csvPath):
        self.X_Data, self.Y_Data = self.read_csv(csvPath)
        self.read_csv(csvPath)
        self.SamplingRate = self.estimate_sampling_rate()    
        ## inits
        self.X_Data_Filtered, self.Y_Data_Filtered = None, None
        self.SpliceLocations = None



    # Setup Functions 
    def estimate_sampling_rate(self):
        return 1/np.mean(np.diff(self.X_Data))
    
    def read_csv(self,filepath):
        file = pd.read_csv(filepath)
        x = file.iloc[:,0].to_numpy()
        y = file.iloc[:,1].to_numpy()
        return x,y
    
    # Hard Calculations 

    def calculate_heart_rate(self,method='conv'):
        if method == 'conv':
            pass
                
    def detect_heart_beats(self,method='dynamicThreshold'):
        parser = argparse.ArgumentParser('detect_heartbeats')
        if method == 'dynamicThreshold':
            ###### TEMPORARY DECS
            PRCT = 97
            
            # t = self.active_ecg.X_Data
            # y = self.active_ecg.Y_Data
            # fs = self.active_ecg.Fs
            t = self.X_Data
            y = self.Y_Data
            fs = self.SamplingRate



            ses_len = t[len(t)-1] - t[0] # length of session
            ses_size = len(t) # Size of session in elements
            len_seg = 1

            # Segment into N second windows; whatever user suggests. 
            # Default to 1
            rows = int(np.floor(ses_len/len_seg))
            cols = int(fs*len_seg)
            Time = np.zeros((rows,cols))
            for g in range(0,int(np.floor(ses_len/len_seg))+1):
                det = [i for i in range(int(1+len_seg*(g-1)*fs),int(len_seg*g*fs)+1)]
                Time[g-1,:] = det
            
            # Cast time to int64
            Time = np.int64(Time)
            spks = []
            for g in range(1,Time.shape[0]):
                seg = y[Time[g,:]]
                p = np.percentile(seg,PRCT) # This is the value that becomes the threshold for segment `g`
                spks.append(Time[g][np.where(seg>p)]/fs)
            # unstack the peaks, because it is nested
            spks = np.hstack(spks)
            mSpks = np.copy(spks) # Make a copy of the array.. bc python name refs lol
            mSpks = np.sort(mSpks)
            

            # Now, we look at every single peak, and then find the max and minimum 
            # within a given window. 
            
            # Create a reference table, with [index, t, y]
            ix = [i for i in range(0,t.shape[0])]
            reftable = np.transpose(np.array([ix,t,y]))

            win = 20 # Window size in elements
            nspk = []
            nspk2 = []
            for ix in range(0,mSpks.shape[0]):
                this = reftable[reftable[:,1] == mSpks[ix],:][0]
                winix = np.array([i for i in range(np.int64(this[0] - (win/2)),
                                          np.int64(this[0] + (win/2)))])
                
                window = reftable[winix[winix>0],:]
                m = np.max(window[:,2])
                i = np.argmax(window[:,2])
                nspk.append()
    
    def filter_ECG(self,method='cwt'):
        if method == 'cwt':
            pass


    # Get and Set functions 
    def get_components(self):
        if self.active_version == 'raw':
            return self.X_Data
        elif self.active_version == 'filtered':
            return self.X_Data_Filtered


    


# Debug and testing 

e = ECG("ex.csv")
e.detect_heart_beats()
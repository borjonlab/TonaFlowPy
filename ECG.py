import numpy as np
import pandas as pd 

class ECG:
    def __init__(self,csvPath):
        self.X_Data, self.Y_Data = self.read_csv(csvPath)
        self.read_csv(csvPath)
        self.SamplingRate = self.estimate_sampling_rate()    
        ## inits
        self.X_Data_Filtered, self.Y_Data_Filtered = None
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

    def calculateHeartRate(self,method='dynamicThreshold'):
        if method == 'dynamicThreshold':
            
    
    def filter_ECG(self,method='cwt'):
        if method == 'cwt':
            pass

    


# Debug and testing 

e = ECG("ex.csv")
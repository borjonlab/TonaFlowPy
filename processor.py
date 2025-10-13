import pandas as pd 
from PyQt6.QtWidgets import (QApplication, QFileDialog)
from new import (ECGApplication,BeatDetectionWindow)
from PyQt6.QtCore import pyqtSignal
import sys

class processor:
    def __init__(self):
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        window = ECGApplication()
        window.show()
        sys.exit(app.exec())
    



    def load_csv_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                df = pd.read_csv(file_path)
                # x = df['Time'].values
                # y = df['Y'].values
                x = df.iloc[:,0]
                y = df.iloc[:,1]
                
                self.data = df
                self.X_Data = x
                self.Y_Data = y
                
                self.SamplingRate = self.estimate_sampling_rate()
                self.fs = self.SamplingRate
                
                self.plot_uploaded_data_simple(x, y)
                
                if self.SamplingRate and np.isfinite(self.SamplingRate):
                    self.sampling_rate_label.setText(f"Sampling Rate (Hz): {self.SamplingRate:.1f}")
                
                if self.X_Data is not None and len(self.X_Data) > 1:
                    duration = self.X_Data.iloc[-1] - self.X_Data.iloc[0]
                    self.session_length_label.setText(f"Session Length (s): {duration:.1f}")
                
                self.filename_label.setText(f"Filenam {os.path.basename(file_path)}")
                self.filepath_label.setText(f"Filepath {file_path}")
                

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed: {e}")
        else:
            print("No file selected")



class controller():
    def __init__(self):
        PROCESSOR = processor()
        PROCESSOR.__init__()
        pass












def main():
    cont = controller()
    


if __name__ == "__main__":
    main()
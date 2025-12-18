
from ssqueezepy import cwt, wavelets, Wavelet, icwt
from ssqueezepy.wavelets import center_frequency
from ssqueezepy.utils import make_scales, cwt_scalebounds
import matplotlib.pyplot as plt
from ECG import ECG 


e = ECG()
e.read_csv("ex.csv")
y = e.Y_Data
fs = e.SamplingRate
N = len(y)


highcutoff = 15
lowcutoff = 10


# N = len(self.Y_Data)
# fs = self.SamplingRate

# wavelet = ('morlet',{'mu':10})
wavelet = Wavelet('morlet')

print("changed")
# Calculate cutoffs in scales 

highcut_scale = (center_frequency(wavelet) * fs) / highcutoff
lowcut_scale = (center_frequency(wavelet) * fs) / lowcutoff

scales_filtered = make_scales(N, scaletype='log', nv=32, max_scale = lowcut_scale,min_scale = highcut_scale)
# Calculate
Wx, _ = cwt(y, wavelet, scales = scales_filtered)
YRec = icwt(Wx, wavelet, scales_filtered)

plt.figure()
plt.plot(YRec)
plt.plot(y)
plt.show()
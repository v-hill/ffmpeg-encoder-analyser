# Python libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ------------------------------- Results plot --------------------------------

data = pd.read_csv('encoding_results.csv')

fig = plt.figure(figsize=(5,4), dpi=400)
ax = fig.add_subplot(111)

plt.plot(data['libx264'].values,data['libx264_ssim'].values, '-.', label='libx264 (CPU)', linewidth=2.2)
plt.plot(data['h264_nvenc'].values,data['h264_nvenc_ssim'].values, '-.', label='h264_nvenc', linewidth=2.2)

plt.plot(data['libx265'].values,data['libx265_ssim'].values, '--', label='libx265 (CPU)', linewidth=2.2)
plt.plot(data['hevc_nvenc'].values,data['hevc_nvenc_ssim'].values, '--', label='hevc_nvenc', linewidth=2.2)

plt.plot(data['libaom-av1'].values,data['libaom-av1_ssim'].values, ':', label='libaom-av1 (CPU)', linewidth=2.2)

major_ticks = np.arange(0, 1.06E5, 20000)
minor_ticks = np.arange(0, 1.06E5, 5000)
ax.set_xticks(major_ticks)
ax.set_xticks(minor_ticks, minor=True)

major_ticks = np.arange(0.95, 0.985, 0.01)
minor_ticks = np.arange(0.95, 0.985, 0.001)
ax.set_yticks(major_ticks)
ax.set_yticks(minor_ticks, minor=True)

ax.grid(which='minor', alpha=0.2)
ax.grid(which='major', alpha=0.5)

plt.xlim([5000, 1.05E5])
plt.ylim([0.95, 0.985])
plt.title('Comparison of FFmpeg video encoders')
plt.xlabel('Bitrate (kbit/s)')
plt.ylabel('SSIM')
plt.legend(loc='lower right')
plt.show()

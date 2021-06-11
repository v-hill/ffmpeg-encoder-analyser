"""
Get bitrate of the test clip and generate a set of new test bitrates.
"""

# Standard library imports
import os
import subprocess
import json
import numpy as np

# -----------------------------------------------------------------------------

work_dir = ""

files = ['']

codecs_h264 = {'libx264' : 'libx264 H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 (codec h264)',
               'h264_nvenc' : 'NVIDIA NVENC H.264 encoder (codec h264)',
               'h264_qsv' : 'H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 (Intel Quick Sync Video acceleration) (codec h264)'}

codecs_h265 = {'libx265' : 'libx265 H.265 / HEVC (codec hevc)',
               'hevc_nvenc' : 'NVIDIA NVENC hevc encoder (codec hevc)',
               'hevc_qsv' : 'HEVC (Intel Quick Sync Video acceleration) (codec hevc)'}

# -----------------------------------------------------------------------------

def make_command(input_file, output_file, encoder, bitrate):
    command = (f'ffmpeg -i "{input_file}" ',
               f'-c:v {encoder} -b:v {bitrate}k -minrate {int(bitrate/2)}k ',
               '-c:a aac -b:a 256k -map_metadata 0 ',
               f'"{output_file}" ')
    return command
    
def get_stats_ffprobe(input_path, work_dir):
    command = ('ffprobe -loglevel 0 -print_format json -show_format -show_streams '
               f'"{os.path.normpath(input_path)}"')
    result = subprocess.run(command, capture_output=True, text=True)
    json_out = json.loads(result.stdout)
    return json_out

def np_round_signif(x, p):
    x_positive = np.where(np.isfinite(x) & (x != 0), np.abs(x), 10**(p-1))
    mags = 10 ** (p - 1 - np.floor(np.log10(x_positive)))
    return np.round(x * mags) / mags

# -----------------------------------------------------------------------------

input_path = files[0]

json_stats = get_stats_ffprobe(input_path, work_dir)
video_stream = json_stats['streams'][0]

orig_bitrate = round(float(video_stream["bit_rate"])/1000,2)
print(f'original bitrate: {orig_bitrate} kbit/s')

test_bitrates = np.linspace(orig_bitrate/2,orig_bitrate,6)
test_bitrates = np_round_signif(test_bitrates, 3) # Round to 3 sig fig

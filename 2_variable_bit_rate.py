"""
Get bitrate of the test clip and generate a set of new test bitrates.
"""

# Standard library imports
import os
import subprocess
import json
import numpy as np
import pickle

# -----------------------------------------------------------------------------

codecs_h264 = {'libx264' : 'libx264 H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 (codec h264)',
               'h264_nvenc' : 'NVIDIA NVENC H.264 encoder (codec h264)',
               'h264_qsv' : 'H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 (Intel Quick Sync Video acceleration) (codec h264)'}

codecs_h265 = {'libx265' : 'libx265 H.265 / HEVC (codec hevc)',
               'hevc_nvenc' : 'NVIDIA NVENC hevc encoder (codec hevc)',
               'hevc_qsv' : 'HEVC (Intel Quick Sync Video acceleration) (codec hevc)'}

# -----------------------------------------------------------------------------

def generate_filename(input_path, output_dir, bitrate, encoder):
    if input_path.count('.')>=2:
        raise Exception('Filename has multiple full stops')
    output_video = input_path.split('/')[-1].replace('.',  f'_{encoder}_{int(bitrate)}.')
    output_path = output_dir+output_video
    return output_path

def make_command(input_file, output_path, encoder, bitrate):
    command = (f'ffmpeg -i "{os.path.normpath(input_file)}" '
               f'-c:v {encoder} -b:v {int(bitrate)}k '
               '-c:a aac -map_metadata 0 '
               f'"{os.path.normpath(output_path)}" ')
    return command
    
def get_stats_ffprobe(input_path):
    command = ('ffprobe -loglevel 0 -print_format json -show_format -show_streams '
               f'"{os.path.normpath(input_path)}"')
    result = subprocess.run(command, capture_output=True, text=True)
    json_out = json.loads(result.stdout)
    return json_out

def np_round_signif(x, p):
    x_positive = np.where(np.isfinite(x) & (x != 0), np.abs(x), 10**(p-1))
    mags = 10 ** (p - 1 - np.floor(np.log10(x_positive)))
    result = np.round(x * mags) / mags
    return result.astype(int)

# -----------------------------------------------------------------------------

work_dir = "U:/....."
filepaths = pickle.load(open(work_dir+"filepaths.pkl", "rb" ))
input_path = filepaths['original']

stats_json = get_stats_ffprobe(input_path)
stats_video_stream = stats_json['streams'][0]

bitrate_orig = round(float(stats_video_stream["bit_rate"])/1000,2)
print(f'original bitrate: {bitrate_orig} kbit/s')
bitrate_tests = np.linspace(bitrate_orig/2,bitrate_orig,6)
bitrate_tests = np.arange(10000,100001,10000)
bitrate_tests = np_round_signif(bitrate_tests, 3) # Round to 3 sig fig


encoder = 'hevc_nvenc'
for bitrate in bitrate_tests:
    output_path = generate_filename(input_path, work_dir, bitrate, encoder)
    filepaths[bitrate] = output_path
    command = make_command(input_path, output_path, encoder, bitrate)
    os.system(command)

pickle.dump(filepaths, open(work_dir+"filepaths.pkl", "wb" ))

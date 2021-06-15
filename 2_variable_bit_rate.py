"""
Get bitrate of the test clip and generate a set of new videos at test bitrates.
"""

# Standard library imports
import os
import subprocess
import json
import pickle
import numpy as np

# -------------------------- FFmpeg encoder examples --------------------------

codecs_h264 = {'libx264' : 'libx264 H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 (codec h264)',
               'h264_nvenc' : 'NVIDIA NVENC H.264 encoder (codec h264)',
               'h264_qsv' : ('H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 '
                             '(Intel Quick Sync Video acceleration) (codec h264)')}

codecs_h265 = {'libx265' : 'libx265 H.265 / HEVC (codec hevc)',
               'hevc_nvenc' : 'NVIDIA NVENC hevc encoder (codec hevc)',
               'hevc_qsv' : 'HEVC (Intel Quick Sync Video acceleration) (codec hevc)'}

# ---------------------------- Function definitions ---------------------------

def generate_filename(in_path, out_dir, bitrate, encoder):
    """
    Create a new filename based on the original video file and test bitrate.

    Parameters
    ----------
    in_path : str
        Full path of input video.
    out_dir : str
        Directory of output video.
    bitrate : int
        Video bitrate in kbit/s.
    encoder : str
        Encoder for FFmpeg to use.

    Returns
    -------
    out_path : str
        Full path of new output video.
    """
    if in_path.count('.') >= 2:
        raise Exception('Filename has multiple full stops')
    out_video = in_path.split('/')[-1].replace('.', f'_{encoder}_{int(bitrate)}.')
    out_path = out_dir+out_video
    return out_path

def make_command(in_file, out_path, encoder, bitrate):
    """
    Make the FFmpeg command.

    Parameters
    ----------
    in_path : str
        Full path of input video.
    out_path : str
        Full path of output video.
    encoder : str
        Name of encoder for FFmpeg to use.
    bitrate : int, float
        Video bitrate to target in kbit/s.

    Returns
    -------
    command : str
        The FFmpeg command to run.
    """
    command = f'ffmpeg -hide_banner -i "{os.path.normpath(in_file)}" '
    if encoder == 'libsvtav1':
        command += f'-c:v {encoder} -rc vbr -b:v {int(bitrate)}k '
    elif encoder == 'libaom-av1':
        command += f'-c:v {encoder} -cpu-used 3 -b:v {int(bitrate)}k '
    else:
        command += f'-c:v {encoder} -b:v {int(bitrate)}k '
    command += '-c:a aac -map_metadata 0 "{os.path.normpath(out_path)}" '
    return command

def get_stats_ffprobe(in_path):
    """
    Use ffprobe to get the info on a video in json format.

    Parameters
    ----------
    in_path : str
        Full path of input video.

    Returns
    -------
    json_out : dict
        Dictionary of video infomation.
    """
    command = ('ffprobe -loglevel 0 -print_format json -show_format '
               f'-show_streams "{os.path.normpath(in_path)}"')
    result = subprocess.run(command, capture_output=True, text=True)
    json_out = json.loads(result.stdout)
    return json_out

def np_round_signif(x, p):
    """
    Given a (n,) dimension numpy array, round each element to 'p' significant 
    figures.

    Parameters
    ----------
    x : numpy.ndarray
        Input array of (n,) shape.
    p : int
        Number of significant figures.

    Returns
    -------
    numpy.ndarray
        Rounded numpy array.
    """
    x_positive = np.where(np.isfinite(x) & (x != 0), np.abs(x), 10**(p-1))
    mags = 10 ** (p - 1 - np.floor(np.log10(x_positive)))
    result = np.round(x * mags) / mags
    return result.astype(int)

# ------------------------------------ Main -----------------------------------

if __name__ == "__main__":
    work_dir = "U:/....."
    filepaths = pickle.load(open(work_dir+"filepaths.pkl", "rb"))
    input_path = filepaths['original']
    
    stats_json = get_stats_ffprobe(input_path)
    stats_video_stream = stats_json['streams'][0]
    
    bitrate_orig = round(float(stats_video_stream["bit_rate"])/1000, 2)
    print(f'original bitrate: {bitrate_orig} kbit/s')
    bitrate_tests = np.linspace(bitrate_orig/2, bitrate_orig, 6)
    bitrate_tests = np.arange(10000, 100001, 10000)
    bitrate_tests = np_round_signif(bitrate_tests, 3) # Round to 3 sig fig
    
    encoder = 'libx265'
    for bitrate in bitrate_tests:
        output_path = generate_filename(input_path, work_dir, bitrate, encoder)
        filepaths[bitrate] = output_path
        command = make_command(input_path, output_path, encoder, bitrate)
        print(command)
        os.system(command)
    
    pickle.dump(filepaths, open(work_dir+"filepaths.pkl", "wb"))
    

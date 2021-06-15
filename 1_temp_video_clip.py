"""
Create a temporary video for analysis.
"""

# Standard library imports
import os
import pickle
import pywintypes, win32file, win32con

# ---------------------------- Function definitions ---------------------------

def make_command(in_path, out_path, duration, start=0):
    """
    Make the FFmpeg command.

    Parameters
    ----------
    in_path : str
        Full path of input video.
    out_path : str
        Full path of output video.
    duration : int
        Duration of test video in seconds.
    start : int, optional
        Specifiy start of test video in seconds. The default is 0.

    Returns
    -------
    command : str
        The FFmpeg command to run.
    """
    in_path = os.path.normpath(in_path)
    out_path = os.path.normpath(out_path)
    if start > 0:
        command = f'ffmpeg -hide_banner -ss {int(start)} -i "{in_path}" '
    else:
        command = f'ffmpeg -hide_banner -i "{in_path}" '
    command += (f'-t {int(duration)} -map_metadata 0 -c copy '
                f'"{out_path}" ')
    print(command)
    return command

def generate_filename(in_path, output_dir):
    """
    Create the filename of the new test video clip.

    Parameters
    ----------
    in_path : str
        Full path of input video.
    output_dir : str
        Directory of output video.

    Returns
    -------
    out_path : str
        Full path of output video.
    """
    if in_path.count('.') >= 2:
        raise Exception('Filename has multiple full stops')
    output_video = in_path.split('/')[-1].replace('.', '_test.')
    out_path = output_dir+output_video
    return out_path

def make_clip(in_path, out_path, duration, start=0):
    """
    Create the FFmpeg command and run it in a subshell.

    Parameters
    ----------
    in_path : str
        Full path of input video.
    out_path : str
        Full path of output video.
    start : int, optional
        Specifiy start of test video in seconds. The default is 0.
    duration : int
        Duration of test video in seconds.
    """
    command = make_command(in_path, out_path, duration, start=start)
    os.system(command)
    
def reset_file_ctime(in_path, out_path):
    """
    Keep the original creation time of the file, but set the modified time to
    current date.

    Parameters
    ----------
    in_path : str
        Full path of input video.
    out_path : str
        Full path of output video.
    """
    ctime = os.path.getctime(in_path)
    mtime = os.path.getmtime(in_path)
    new_time = min(ctime, mtime)
    orig_time = os.path.getmtime(out_path)
    wintime1 = pywintypes.Time(new_time)
    winfile = win32file.CreateFile(out_path, win32con.GENERIC_WRITE,
                                   win32con.FILE_SHARE_READ | 
                                   win32con.FILE_SHARE_WRITE | 
                                   win32con.FILE_SHARE_DELETE,
                                   None, 
                                   win32con.OPEN_EXISTING,
                                   win32con.FILE_ATTRIBUTE_NORMAL, 
                                   None)

    win32file.SetFileTime(winfile, wintime1, wintime1, wintime1)
    winfile.close()
    os.utime(out_path, (orig_time, orig_time))

# ------------------------------------ Main -----------------------------------

if __name__ == "__main__":
    input_dir = "E:/....."
    input_video = ""
    input_path = input_dir + input_video
    work_dir = "U:/....."
    filepaths = {}
    
    clip_start = 0    #seconds
    clip_length = 30    #seconds
    
    output_path = generate_filename(input_path, work_dir)
    filepaths['original'] = output_path
    make_clip(input_path, output_path, clip_length, start=clip_start)
    reset_file_ctime(input_path, output_path)
    
    pickle.dump(filepaths, open(work_dir+"filepaths.pkl", "wb"))
    

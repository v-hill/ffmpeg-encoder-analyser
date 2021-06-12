"""
Create a temporary video for analysis.
"""

# Standard library imports
import os
import time
import datetime
import pickle
import pywintypes, win32file, win32con

# -----------------------------------------------------------------------------

def get_timestamp(input_path):
    creation_time = time.ctime(os.path.getmtime(input_path))
    creation_time = creation_time[4:]
    new_creation = datetime.datetime.strptime(creation_time, '%b %d %H:%M:%S %Y')
    new_creation = f"{new_creation:%Y-%m-%dT%H:%M:%S.000000Z}"
    print(f"Old: {creation_time},    New: {new_creation}")
    return new_creation

def make_command(input_file, output_file, start, duration):
    input_file = os.path.normpath(input_file)
    output_file = os.path.normpath(output_file)
    if start>0:
        command = f'ffmpeg -hide_banner -ss {int(start)} -i "{input_file}" '
    else:
        command = f'ffmpeg -hide_banner -i "{input_file}" '
    command += (f'-t {int(duration)} -map_metadata 0 '
                '-c copy '
                f'"{output_file}" ')
    print(command)
    return command

def generate_filename(input_path, output_dir):
    if input_path.count('.')>=2:
        raise Exception('Filename has multiple full stops')
    output_video = input_path.split('/')[-1].replace('.', '_test.')
    output_path = output_dir+output_video
    return output_path

def make_clip(input_path, output_path, start, duration):
    command = make_command(input_path, output_path, start, duration)
    os.system(command)
    
def reset_file_ctime(input_path, output_path):
    """
    Keep the original creation time of the file, but set the modified time to
    current date.
    """
    ctime = os.path.getctime(input_path)
    mtime = os.path.getmtime(input_path)
    new_time = min(ctime, mtime)
    orig_time = os.path.getmtime(output_path)
    wintime1 = pywintypes.Time(new_time)
    winfile = win32file.CreateFile(output_path, win32con.GENERIC_WRITE,
                                   win32con.FILE_SHARE_READ | 
                                   win32con.FILE_SHARE_WRITE | 
                                   win32con.FILE_SHARE_DELETE,
                                   None, 
                                   win32con.OPEN_EXISTING,
                                   win32con.FILE_ATTRIBUTE_NORMAL, 
                                   None)

    win32file.SetFileTime(      winfile,  wintime1,  wintime1,     wintime1)
    winfile.close()
    os.utime(output_path, (orig_time, orig_time))

# -----------------------------------------------------------------------------

"""
Only run as a command line program.
"""

if __name__ == "__main__":
    input_dir = "E:/....."
    input_video = ""
    input_path = input_dir + input_video
    work_dir = "U:/....."
    filepaths = {}
    
    start = 0    #seconds
    duration = 120    #seconds
    
    output_path = generate_filename(input_path, work_dir)
    filepaths['original'] = output_path
    make_clip(input_path, output_path, start, duration)
    reset_file_ctime(input_path, output_path)
    
    pickle.dump(filepaths, open(work_dir+"filepaths.pkl", "wb" ))
    

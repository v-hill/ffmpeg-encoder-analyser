"""
Create a temporary video for analysis.
"""

# Standard library imports
import os
import time
import datetime

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
        command = f'ffmpeg -ss {int(start)} -i "{input_file}" '
    else:
        command = f'ffmpeg -i "{input_file}" '
    command += (f'-t {int(duration)} -map_metadata 0 -c copy '
                f'"{output_file}" ')
    print(command)
    return command

def generate_filename(input_path, output_dir):
    output_video = input_path.split('/')[-1].replace('.mp4', '_short.mp4')
    output_path = output_dir+output_video
    return output_path

def make_clip(output_path, start, duration):
    command = make_command(input_dir+input_video, output_path, start, duration)
    os.system(command)
    stinfo = os.stat(input_path)
    os.utime(output_path,(stinfo.st_atime, stinfo.st_mtime))
    
# -----------------------------------------------------------------------------

"""
Only run as a command line program.
"""

if __name__ == "__main__":
    input_dir = ""
    input_video = ""
    input_path = input_dir + input_video
    output_dir = ""
    
    start = 330    #seconds
    duration = 120    #seconds
    
    files = []
    
    output_path = generate_filename(input_path, output_dir)
    files.append(output_path)
    make_clip(output_path, start, duration)

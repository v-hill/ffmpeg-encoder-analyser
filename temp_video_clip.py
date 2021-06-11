
"""
Create a temporary video for analysis.
"""

# Standard library imports
import os
import time
import datetime

# -----------------------------------------------------------------------------

def get_timestamp(input_name):
    creation_time = time.ctime(os.path.getmtime(input_name))
    creation_time = creation_time[4:]
    new_creation = datetime.datetime.strptime(creation_time, '%b %d %H:%M:%S %Y')
    new_creation = f"{new_creation:%Y-%m-%dT%H:%M:%S.000000Z}"
    print(f"Old: {creation_time},    New: {new_creation}")
    return new_creation

def make_command(input_file, output_file, start, duration):
    if start>0:
        command = f'ffmpeg -ss {int(start)} -i "{input_file}" '
    else:
        command = f'ffmpeg -i "{input_file}" '
    command += f'-t {int(duration)} -c copy '
    command += f'"{output_file}"'
    return command

def generate_filename(input_name, output_dir):
    output_video = input_name.split('\\')[-1].replace('.mp4', '_short.mp4')
    output_name = output_dir+output_video
    return output_name

    
def make_clip(output_name, start, duration):

    command = make_command(input_dir+input_video, output_name, start, duration)
    
    os.system(command)
    stinfo = os.stat(input_name)
    os.utime(output_name,(stinfo.st_atime, stinfo.st_mtime))
    
# -----------------------------------------------------------------------------

"""
Only run as a command line program.
"""

if __name__ == "__main__":
    input_dir = ""
    input_video = ""
    input_name = input_dir + input_video
    output_dir = ""
    
    start = 330    #seconds
    duration = 120    #seconds
    
    files = []
    
    output_name = generate_filename(input_name, output_dir)
    files.append(output_name)
    make_clip(output_name, start, duration)

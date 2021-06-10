"""
Create a temporary video for analysis.
"""

import os
import os.path
import time
from glob import glob
import datetime
import cv2

# -----------------------------------------------------------------------------

def get_timestamp(input_name):
    creation_time = time.ctime(os.path.getmtime(input_name))
    creation_time = creation_time[4:]
    new_creation = datetime.datetime.strptime(creation_time, '%b %d %H:%M:%S %Y')
    new_creation = f"{new_creation:%Y-%m-%dT%H:%M:%S.000000Z}"
    print(f"Old: {creation_time},    New: {new_creation}")
    return new_creation

def make_command(input_file, output_file, start, duration):
    command = f'ffmpeg -ss {int(start)} -i "{input_file}" '
    command += f'-t {int(duration)} -c copy '
    command += f'"{output_file}"'
    return command

# -----------------------------------------------------------------------------

input_dir = ""
input_video = ""

output_dir = ""

start = 330    #seconds
duration = 120    #seconds

files = []

input_name = input_dir + input_video
output_video = input_name.split('\\')[-1].replace('.mp4', '_short.mp4')
output_name = output_dir+output_video
files.append(output_name)

command = make_command(input_dir+input_video, output_name, start, duration)
print(command)

os.system(command)
stinfo = os.stat(input_name)
os.utime(output_name,(stinfo.st_atime, stinfo.st_mtime))

time.sleep(5)
for f in files:
    os.remove(f)

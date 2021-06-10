
"""
Create a temporary video for analysis.
"""

import os
import os.path, time
from glob import glob
import datetime
import cv2

input_dir = ""
input_video = ""
output_dir = ""

def make_command(input_file, output_file, start, duration):
    command = f'ffmpeg -ss {int(start)} -i "{input_file}" '
    command += f'-t {int(duration)} -c copy '
    command += f'"{output_file}"'
    return command

start = 390    #seconds
duration = 120    #seconds

input_name = input_dir + input_video
output_video = input_name.split('\\')[-1].replace('.mp4', '_short.mp4')

command = make_command(input_dir+input_video, output_dir+output_video, start, duration)
print(command)

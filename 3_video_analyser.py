"""
Compute the structural similarity (SSIM) index for each test video.
"""

# Standard library imports
import cv2
import numpy as np
import os
import pandas as pd
import pickle
from skimage import img_as_float
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error
import subprocess
import time

# ---------------------------- Function definitions ---------------------------

def create_images(filepath, work_dir, frame_interval, new=True):
    if new:
        command = (f'ffmpeg -hide_banner -i "{filepath}" -r 1/{frame_interval}'
                    f' "{work_dir}new_%03d.bmp"')
    else:
        command = (f'ffmpeg -hide_banner -i "{filepath}" -r 1/{frame_interval}'
            f' "{work_dir}old_%03d.bmp"')
    os.system(command)

    
def get_bitrate(input_path):
    
    command = ('ffprobe -v error -select_streams v:0 -show_entries stream=bit_rate'
               f' -of default=noprint_wrappers=1:nokey=1 "{os.path.normpath(input_path)}"')

    result = subprocess.run(command, capture_output=True, text=True)
    result = result.stdout
    bitrate = result.replace('\n','')
    bitrate = round(float(bitrate)/1000,2)

    return bitrate

# ------------------------------------ Main -----------------------------------

work_dir = "U:/....."
filepaths = pickle.load(open(work_dir+"filepaths.pkl", "rb" ))

bitrates = list(filepaths.keys())
bitrates = [rate for rate in bitrates if isinstance(rate, np.int32)]
frame_interval = 1 #seconds

all_results = []

TIME = time.time()
filepath_orig = filepaths['original']
create_images(filepath_orig, work_dir, frame_interval, new=False)
for bitrate in bitrates:
    filepath_test = filepaths[bitrate]
    real_bitrate = get_bitrate(filepath_test)
    print(f'target bitrate: {bitrate}, real bitrate: {real_bitrate}')
    create_images(filepath_test, work_dir, frame_interval)
    
    mse_results = []
    ssim_results = []
    image_files = os.listdir(work_dir)
    image_files = [f for f in image_files if 'bmp' in f]
    new_images = [f for f in image_files if 'new' in f]
    old_images = [f for f in image_files if 'old' in f]
    
    for index, (old_im, new_im) in enumerate(zip(new_images, old_images)):
        
        img1 = cv2.imread(work_dir+old_im)
        img2 = cv2.imread(work_dir+new_im)
        psnr = cv2.PSNR(img1, img2)
    
        img1 = img_as_float(img1)
        img2 = img_as_float(img2)
        
        mse_val = mean_squared_error(img1, img2)
        ssim_val = ssim(img1, img2, data_range=img2.max() - img2.min(), multichannel=True)
        mse_results.append(mse_val)
        ssim_results.append(ssim_val)
        # print(f'{index},{mse_val:0.7f},{ssim_val:0.4f}')
        
    mse_results = np.asarray(mse_results)
    ssim_results = np.asarray(ssim_results)
    
    result = {'bitrate target' : bitrate,
              'bitrate real' : real_bitrate,
              'ssim_mean' : np.mean(ssim_results),
              'mse_mean' : np.mean(mse_results),
              'ssim_median' : np.median(ssim_results),
              'mse_median' : np.median(mse_results)}
    
    all_results.append(result)
    print(f'{bitrate},{np.mean(mse_results):0.7f},{np.mean(ssim_results):0.4f}')
    print(f'{bitrate},{np.median(mse_results):0.7f},{np.median(ssim_results):0.4f}')
        
    for f in new_images:
        os.remove(work_dir+f)
        
    df = pd.DataFrame(all_results)
    df.to_csv(work_dir+'image_quality_results.csv', index=False)

for f in old_images:
    os.remove(work_dir+f)

print(f'elapsed time: {time.time() - TIME:0.3f}s')

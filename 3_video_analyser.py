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


def create_images(in_path, work_dir, frame_interval, new=True):
    """
    Given the filepath to a video, capture image frames at a specified frame
    interval and save the images to the work directory.

    Parameters
    ----------
    in_path : str
        Full path of input video.
    work_dir : str
        Directory to ouptut the image files.
    frame_interval : int
        Capture an image every frame_interval number of seconds.
    new : bool, optional
        Specifies if the video is the original or encoded video.
        The default is True.
    """
    if new:
        command = (f'ffmpeg -hide_banner -i "{in_path}" -r 1/{frame_interval}'
                   f' "{work_dir}new_%03d.bmp"')
    else:
        command = (f'ffmpeg -hide_banner -i "{in_path}" -r 1/{frame_interval}'
                   f' "{work_dir}old_%03d.bmp"')
    os.system(command)


def get_bitrate(in_path):
    """
    Given the path to a video, return the video bitrate using ffprobe.

    Parameters
    ----------
    in_path : str
        Full path of input video.

    Returns
    -------
    bitrate : float
        Video bitrate in kbit/s.
    """
    command = ('ffprobe -v error -select_streams v:0 -show_entries '
               'stream=bit_rate -of default=noprint_wrappers=1:nokey=1 '
               f'"{os.path.normpath(in_path)}"')
    vid_info = subprocess.run(command, capture_output=True, text=True)
    vid_info = vid_info.stdout
    bitrate = vid_info.replace('\n', '')
    bitrate = round(float(bitrate) / 1000, 2)
    return bitrate


def analyse_images(new_images, old_images, verbose=False):
    """
    Iterate through the set of images and calculate the Structural Similarity
    Index (SSIM) and mean squared error (MSE).

    Parameters
    ----------
    new_images : list
        The list of encoded images.
    old_images : list
        The list of images from the original video.
    verbose : bool, optional
        Print the results of each frame. The default is False.

    Returns
    -------
    mse_results : list
        List of MSE values for each frame.
    ssim_results : list
        List of SSIM values for each frame.
    """
    mse_results = []
    ssim_results = []
    for index, (old_im, new_im) in enumerate(zip(new_images, old_images)):
        img1 = cv2.imread(WORK_DIR + old_im)
        img2 = cv2.imread(WORK_DIR + new_im)
        # psnr = cv2.PSNR(img1, img2)

        img1 = img_as_float(img1)
        img2 = img_as_float(img2)

        mse_val = mean_squared_error(img1, img2)
        ssim_val = ssim(
            img1,
            img2,
            data_range=img2.max() -
            img2.min(),
            multichannel=True)
        mse_results.append(mse_val)
        ssim_results.append(ssim_val)
        if verbose:
            print(f'{index},{mse_val:0.7f},{ssim_val:0.4f}')
    return mse_results, ssim_results

# ------------------------------------ Main -----------------------------------


WORK_DIR = "U:/....."
filepaths = pickle.load(open(WORK_DIR + "filepaths.pkl", "rb"))

bitrates = list(filepaths.keys())
bitrates = [rate for rate in bitrates if isinstance(rate, np.int32)]
frame_interval = 1  # seconds
all_results = []
filepath_orig = filepaths['original']

TIME = time.time()  # Start timer
create_images(filepath_orig, WORK_DIR, frame_interval, new=False)

for bitrate in bitrates:
    filepath_test = filepaths[bitrate]
    real_bitrate = get_bitrate(filepath_test)
    print(f'target bitrate: {bitrate}, real bitrate: {real_bitrate}')
    create_images(filepath_test, WORK_DIR, frame_interval)

    image_files = [f for f in os.listdir(WORK_DIR) if 'bmp' in f]
    new_images = [f for f in image_files if 'new' in f]
    old_images = [f for f in image_files if 'old' in f]

    mse_results, ssim_results = analyse_images(new_images, old_images)
    mse_results = np.asarray(mse_results)
    ssim_results = np.asarray(ssim_results)

    result = {'bitrate target': bitrate,
              'bitrate real': real_bitrate,
              'ssim_mean': np.mean(ssim_results),
              'mse_mean': np.mean(mse_results),
              'ssim_median': np.median(ssim_results),
              'mse_median': np.median(mse_results)}
    all_results.append(result)
    print(f'{bitrate},{np.mean(mse_results):0.7f},{np.mean(ssim_results):0.4f}')
    # print(f'{bitrate},{np.median(mse_results):0.7f},{np.median(ssim_results):0.4f}')

    df = pd.DataFrame(all_results)
    df.to_csv(WORK_DIR + 'image_quality_results.csv', index=False)

    for f in new_images:
        os.remove(WORK_DIR + f)  # Tidy up work directory

for f in old_images:
    os.remove(WORK_DIR + f)  # Tidy up work directory

print(f'elapsed time: {time.time() - TIME:0.3f}s')

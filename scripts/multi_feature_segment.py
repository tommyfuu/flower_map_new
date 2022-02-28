#!/usr/bin/env python3
import argparse
from pathlib import Path

# revised from arya's script segment.py

parser = argparse.ArgumentParser(
    description=
    """
        Segment the image into objects and output both 1) contours which we are
        highly confident have plants and 2) contours which we have less
        confidence contain plants (where the contours from #1 are contained
        within the regions outlined by #2). You can run watershed.py with #1 and
        #2 to get the resulting contours.
    """
)
parser.add_argument(
    "image", help="a path to the image to segment"
)
parser.add_argument(
    "out_high", help="the path to a file in which to store the coordinates of each extracted high confidence object"
)
parser.add_argument(
    "out_low", help="the path to a file in which to store the coordinates of each extracted low confidence object"
)
parser.add_argument(
    "--texture-cache", type=Path, help=
    """
        The path to an npy file containing the texture of the image if already calculated.
        (Providing this option can speed up repeated executions of this script on the same input.)
        If this file does not exist, it will be created when the texture is calculated.
    """
)
args = parser.parse_args()
if not (
    (args.out_high.endswith('.json') or args.out_high.endswith('.npy')) and
    (args.out_low.endswith('.json') or args.out_low.endswith('.npy'))
):
    parser.error('Unsupported output file type. The files must have a .json or .npy ending.')

import features
import cv2 as cv
import numpy as np
import scipy.ndimage

# CONSTANTS
PARAMS = {
    'texture': {
        'window_radius': 2,
        'num_features': 6,
        'inverse_resolution': 30
    },
    'blur': {
        'green_kernel_size': 5,
        'green_strength': 60,
        'contrast_kernel_size': 24
    },
    'noise_removal': {
        'strength': 17,
        'templateWindowSize': 7,
        'searchWindowSize': 21
    },
    'threshold': {
        'block_size': 25,
        'C': 10,
    },
    'morho': {
        'big_kernel_size': 24,
        'small_kernel_size': 5,
        'high': {
            'closing': 7,
            'opening': 4+15
        },
        'low': {
            'closing': 7,
            'opening': 4+7,
            'closing2': 14
        }
    }
}

def sliding_window(img, fnctn, size, num_features=1, skip=0):
    """
        run fnctn over each sliding, square window of width 2*size+1, skipping every skip pixel
        store the result in a np arr of equal size as the img but with depth equal to num_features
    """
    # make a shape x num_features array, since there are num_features features
    new = np.empty(img.shape+(num_features,))
    # run a sliding window over the i and j indices
    for i in range(0, img.shape[0], skip):
        # we adjust for windows that would otherwise go over the edge of the frame
        i1 = max(0, i-size)
        i2 = min(i+size+1, img.shape[0])
        next_i = min(i+skip, img.shape[0])
        for j in range(0, img.shape[1], skip):
            j1 = max(0, j-size)
            j2 = min(j+size+1, img.shape[1])
            next_j = min(j+skip, img.shape[1])
            # call the function
            new[i:next_i,j:next_j,:] = fnctn(img[i1:i2,j1:j2])
    return new


print('loading image')
img = cv.imread(args.image)

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
if args.texture_cache is not None and args.texture_cache.exists():
    print('loading texture from cached file')
    texture = np.load(args.texture_cache)
else:
    print('calculating texture (this may take a while)')
    texture = sliding_window(gray, features.glcm, *tuple([PARAMS['texture'][i] for i in ['window_radius', 'num_features', 'inverse_resolution']]))
    if args.texture_cache is not None:
        args.texture_cache.parents[0].mkdir(parents=True, exist_ok=True)
        np.save(args.texture_cache, texture)

# blur image to remove noise from grass
print('blurring image to remove noise in the green and contrast values')
blur_colors = cv.GaussianBlur(img, (PARAMS['blur']['green_kernel_size'],)*2, PARAMS['blur']['green_strength'])

# 1. get all feature values
## colors; note that opencv uses bgr color format
blur_blue = blur_colors[:,:,0]
blur_green = blur_colors[:,:,1]
blur_red = blur_colors[:,:,2]

## textural features
blur_gradient = cv.Laplacian(gray, cv.CV_8UC1)
blur_contrast = np.uint8(texture[:,:,0]*255)
blur_correlation = np.uint8(texture[:,:,4]*255)
blur_energy = np.uint8(texture[:,:,3]*255)
blur_homogeneity = np.uint8(texture[:,:,2]*255)


# blur_contrast = np.uint8(cv.blur(texture[:,:,0], (PARAMS['blur']['contrast_kernel_size'],)*2))
# blur_correlation = np.uint8(cv.blur(texture[:,:,4], (PARAMS['blur']['contrast_kernel_size'],)*2)*255)
# blur_energy = np.uint8(cv.blur(texture[:,:,3], (PARAMS['blur']['contrast_kernel_size'],)*2)*255)
# blur_homogeneity = np.uint8(cv.blur(texture[:,:,2], (PARAMS['blur']['contrast_kernel_size'],)*2)*255)

cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_blue_OG.JPG', blur_blue)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_green_OG.JPG', blur_green)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_red_OG.JPG', blur_red)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_gradient_OG.JPG', blur_gradient)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_contrast_OG.JPG', blur_contrast)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_correlation_OG.JPG', blur_correlation)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_energy_OG.JPG', blur_energy)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_homogeneity_OG.JPG', blur_homogeneity)


# 2. adaptive guassian thresholding
th_blue = cv.adaptiveThreshold(blur_blue,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
th_green = cv.adaptiveThreshold(blur_green,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
th_red = cv.adaptiveThreshold(blur_red,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
th_gradient = cv.adaptiveThreshold(blur_gradient,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
th_contrast = cv.adaptiveThreshold(blur_contrast,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
th_correlation = cv.adaptiveThreshold(blur_correlation,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])          
th_energy = cv.adaptiveThreshold(blur_energy,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
th_homogeneity = cv.adaptiveThreshold(blur_homogeneity,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])


cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_blue.JPG', th_blue)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_green.JPG', th_green)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_red.JPG', th_red)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_gradient.JPG', th_gradient)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_contrast.JPG', th_contrast)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_correlation.JPG', th_correlation)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_energy.JPG', th_energy)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_homogeneity.JPG', th_homogeneity)
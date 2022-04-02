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

import statsmodels.api as sm
from scipy import stats
from matplotlib import pyplot as plt
from pycocotools.coco import COCO
import os, sys, zipfile
import matplotlib.pyplot as plt
import pylab
import json


# CONSTANTS
PARAMS = {
    'texture': {
        'window_radius': 2,
        'num_features': 6,
        'inverse_resolution': 50 # arya's value: 30
    },
    'blur': {
        'green_kernel_size': 5,
        'green_strength': 60,
        'contrast_kernel_size': 24 # potentially deletable
    },    
    'threshold': {
        'block_size': 2003,
        'C': 10,
    },
    # Tom's addition:
    'num_of_features': {
        'high': 5,
        'low': 4
    },
    # 'num_of_color_features': {
    #     'high': 3,
    #     'low': 2
    # },
    # 'num_of_texture_features': {
    #     'high': 2,
    #     'low': 1
    # },
    # TODO: will be useful in closing holes
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
        },
        'noise_removal': {
        'strength': 17,
        'templateWindowSize': 7,
        'searchWindowSize': 21
    },
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
print(img.shape)
name_img = str(args.image).split("/")[-1].split(".")[-2]

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
blur_contrast = np.uint8(texture[:,:,0]*255/texture[:,:,0].max())
blur_correlation = np.uint8(texture[:,:,4]*255)
blur_energy = np.uint8(texture[:,:,3]*255/texture[:,:,3].max())
blur_homogeneity = np.uint8(texture[:,:,2]*255)


# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_blue_OG.JPG', blur_blue)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_green_OG.JPG', blur_green)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_red_OG.JPG', blur_red)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_gradient_OG.JPG', blur_gradient)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_contrast_OG.JPG', blur_contrast)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_correlation_OG.JPG', blur_correlation)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_energy_OG.JPG', blur_energy)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_homogeneity_OG.JPG', blur_homogeneity)


# 2. adaptive guassian thresholding
### TODO: as of 3/1 night the only feature that doesn't work at all is correlation.
th_blue = 255- cv.adaptiveThreshold(blur_blue,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
th_green = 255- cv.adaptiveThreshold(blur_green,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
th_red = 255- cv.adaptiveThreshold(blur_red,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
th_gradient = 255- cv.adaptiveThreshold(blur_gradient,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
th_contrast = 255 - cv.adaptiveThreshold(blur_contrast,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
# th_correlation = cv.adaptiveThreshold(blur_correlation,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
#             cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])          
# th_energy = cv.adaptiveThreshold(blur_energy,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
#             cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])
th_homogeneity = 255- cv.adaptiveThreshold(blur_homogeneity,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv.THRESH_BINARY,PARAMS['threshold']['block_size'],PARAMS['threshold']['C'])

# voting scheme
# check to make sure unique values are 0 255


th_blue_1 = th_blue/255
th_green_1 = th_green/255
th_red_1 = th_red/255
th_gradient_1 = th_gradient/255
th_contrast_1 = th_contrast/255
# th_correlation_1 = th_correlation/255
# th_energy_1 = th_energy/255
th_homogeneity_1 = th_homogeneity/255

# sum_thresholds = th_blue_1+th_green_1+th_red_1+th_gradient_1+th_contrast_1+th_correlation_1+th_energy_1+th_homogeneity_1
# sum_thresholds = th_blue_1+th_green_1+th_red_1+th_gradient_1+th_contrast_1+th_homogeneity_1

PARAMS_DICT = {
    "th_blue": 21.838007,
    "th_green": 7.186267,
    "th_red": 35.805404,
    "th_gradient": 43.179289,
    "th_contrast": 26.178679,
    "th_homogeneity": 27.108396,
}
factor=1.0/sum(PARAMS_DICT.values())
for k in PARAMS_DICT:
  PARAMS_DICT[k] = PARAMS_DICT[k]*factor

sum_thresholds = th_blue_1*PARAMS_DICT["th_blue"]+th_green_1*PARAMS_DICT["th_green"]+th_red_1*PARAMS_DICT["th_red"]+th_gradient_1*PARAMS_DICT["th_gradient"]+th_contrast_1*PARAMS_DICT["th_contrast"]+th_homogeneity_1*PARAMS_DICT["th_homogeneity"]

print(np.unique(sum_thresholds))
# according to the two hyperparameters, thresholding
print('thresholding')
# thresh_high = (sum_thresholds > (PARAMS['num_of_features']['high'])) * np.uint8(255)
# # use a lower threshold to create the low confidence regions, so that they are larger
# thresh_low = (sum_thresholds > (PARAMS['num_of_features']['low'])) * np.uint8(255)

thresh_high = (sum_thresholds > (PARAMS['num_of_features']['high']/6)) * np.uint8(255)
thresh_low = (sum_thresholds > (PARAMS['num_of_features']['low']/6)) * np.uint8(255)
print(np.unique(thresh_high))
print(np.unique(thresh_low))

cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_high_OG_' +str(PARAMS['threshold']['block_size'])+ '.JPG', thresh_high)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_low_OG_' +str(PARAMS['threshold']['block_size'])+ '.JPG', thresh_low)

# noise removal
# thresh_high = cv.fastNlMeansDenoising(
#     thresh_high, None, PARAMS['noise_removal']['strength'],
#     PARAMS['noise_removal']['templateWindowSize'], PARAMS['noise_removal']['searchWindowSize']
# )
# thresh_low = cv.fastNlMeansDenoising(
#     thresh_low, None, PARAMS['noise_removal']['strength'],
#     PARAMS['noise_removal']['templateWindowSize'], PARAMS['noise_removal']['searchWindowSize']
# )
print('performing morphological operations and hole filling')

# method 1
# kernel = np.ones((20,20),np.uint8)
kernel = np.ones((15,15),np.uint8)
filled = scipy.ndimage.binary_fill_holes(thresh_high) * np.uint8(255)
high = cv.morphologyEx(filled, cv.MORPH_CLOSE, kernel)
low = cv.morphologyEx(thresh_low, cv.MORPH_CLOSE, kernel)

# method 2
# filled = scipy.ndimage.binary_fill_holes(thresh_high) * np.uint8(255)
# closing_high = cv.morphologyEx(filled, cv.MORPH_CLOSE, kernel)
# filled1 = scipy.ndimage.binary_fill_holes(closing_high) * np.uint8(255)
# high = cv.morphologyEx(filled1, cv.MORPH_CLOSE, kernel)

# closing_low = cv.morphologyEx(thresh_low, cv.MORPH_CLOSE, kernel)
# opening_low = cv.morphologyEx(closing_low, cv.MORPH_OPEN, kernel)
# filled1 = scipy.ndimage.binary_fill_holes(closing_high) * np.uint8(255)
# high = cv.morphologyEx(filled1, cv.MORPH_CLOSE, kernel)


# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'__high_filled_new_' +str(PARAMS['threshold']['block_size'])+ '.JPG', high)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'__low_filled_new_' +str(PARAMS['threshold']['block_size'])+ '.JPG', low)

# high = cv.erode(thresh_high, kernel,iterations = 1)
# low = cv.erode(thresh_low, kernel,iterations = 1)


# first, create the kernels we use in the morpho operations
small_kernel = np.ones((PARAMS['morho']['small_kernel_size'],)*2, np.uint8)
big_kernel = np.ones((PARAMS['morho']['big_kernel_size'],)*2, np.uint8)



# Now, we do morpho operations and hole filling to get the high confidence regions:
# 1) use the fill_holes method to boost background pixels that are surrounded by foreground
filled = scipy.ndimage.binary_fill_holes(thresh_high) * np.uint8(255)
# 2) use closing to boost the size of the regions even more before step 4
closing_high = cv.morphologyEx(
    filled, cv.MORPH_CLOSE, small_kernel, iterations = PARAMS['morho']['high']['closing']
)
# 3) use fill_holes one more time, just in case there's anything else that needs filling
filled1 = scipy.ndimage.binary_fill_holes(closing_high) * np.uint8(255)
# 4) use a lot of morphological opening to keep only the regions that we are highly confident contain plants
high = cv.morphologyEx(
    filled1, cv.MORPH_OPEN, small_kernel, iterations = PARAMS['morho']['high']['opening']
)
# Now, we do morpho operations to get the low confidence regions:
# 1) use closing to boost the size of some of the plants that have a lot of foreground mixed in
closing_low = cv.morphologyEx(
    thresh_low, cv.MORPH_CLOSE, small_kernel, iterations = PARAMS['morho']['low']['closing']
)
# 2) use opening to get rid of the noise
opening_low = cv.morphologyEx(
    closing_low, cv.MORPH_OPEN, small_kernel, iterations = PARAMS['morho']['low']['opening']
)
# 3) use closing again to mostly undo the effects of the opening from before and create low-confidence regions
low = cv.morphologyEx(
    opening_low, cv.MORPH_CLOSE, small_kernel, iterations = PARAMS['morho']['low']['closing2']
)

cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'__high_filled_arya_' +str(PARAMS['threshold']['block_size'])+ '.JPG', high)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'__low_filled_arya_' +str(PARAMS['threshold']['block_size'])+ '.JPG', low)

# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_blue' +str(PARAMS['threshold']['block_size'])+ '.JPG', th_blue)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_green' +str(PARAMS['threshold']['block_size'])+ '.JPG', th_green)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_red' +str(PARAMS['threshold']['block_size'])+ '.JPG', th_red)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_gradient' +str(PARAMS['threshold']['block_size'])+ '.JPG', th_gradient)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_contrast' +str(PARAMS['threshold']['block_size'])+ '.JPG', th_contrast)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_correlation' +str(PARAMS['threshold']['block_size'])+ '.JPG', th_correlation)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_energy' +str(PARAMS['threshold']['block_size'])+ '.JPG', th_energy)
# cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001_homogeneity' +str(PARAMS['threshold']['block_size'])+ '.JPG', th_homogeneity)


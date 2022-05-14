#!/usr/bin/env python3
import argparse
from pathlib import Path
import time
start_time = time.time()
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

# # uncomment this stuff for testing
# from test_util import *
# import matplotlib.pyplot as plt
# plt.ion()


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
    'combine': {
        'green_weight': 0.75,
        'contrast_weight': 0.25
    },
    'noise_removal': {
        'strength': 17,
        'templateWindowSize': 7,
        'searchWindowSize': 21
    },
    'threshold': {
        'high': 0.53,
        'low': 0.53-0.07,
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

name_img = str(args.image).split("/")[-1].split(".")[-2]
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

def green_contrast(
    green, contrast, green_weight=PARAMS['combine']['green_weight'],
    contrast_weight=PARAMS['combine']['contrast_weight']
):
    """ take a weighted average of the green and contrast values for each pixel """
    # normalize the weights, just in case they don't already add to 1
    print("greeness", green.shape, green)
    print("contrast", contrast.shape, contrast)
    total = green_weight + contrast_weight
    green_weight /= total
    contrast_weight /= total
    # normalize the green and contrast values
    green = green / np.max(green)
    contrast = contrast / np.max(contrast)
    return ((1-green)*green_weight) + (contrast*contrast_weight)

def largest_polygon(polygons):
    """ get the largest polygon among the polygons """
    # we should probably use a complicated formula to do this
    # but for now, it probably suffices to notice that the last one is usually
    # the largest
    return polygons.points[-1]

def export_results(mask, out):
    """ write the resulting mask to a file """
    ret, markers = cv.connectedComponents(mask.astype(np.uint8))
    # should we save the segments as a mask or as bounding boxes?
    if out.endswith('.npy'):
        np.save(out, markers)
    elif out.endswith('.json'):
        # import extra required modules
        from imantics import Mask
        import import_labelme
        segments = [
            (int(i), largest_polygon(Mask(markers == i).polygons()).tolist())
            for i in range(1, ret)
        ]
        import_labelme.write(out, segments, args.image)
    else:
        raise Exception("Unsupported output file format.")

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
print("texture.shape", texture.shape, texture)
blur_green = cv.GaussianBlur(img, (PARAMS['blur']['green_kernel_size'],)*2, PARAMS['blur']['green_strength'])
blur_contrast = cv.blur(texture[:,:,0], (PARAMS['blur']['contrast_kernel_size'],)*2)

print('combining green and contrast values and removing more noise')
combined = np.uint8(green_contrast(blur_green[:,:,1], blur_contrast) * 255)

cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_original_segment_combined_.JPG', combined)

combined = cv.fastNlMeansDenoising(
    combined, None, PARAMS['noise_removal']['strength'],
    PARAMS['noise_removal']['templateWindowSize'], PARAMS['noise_removal']['searchWindowSize']
)

cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_original_segment_combined_denoised.JPG', combined)


print('performing greyscale morphological closing')
combined = scipy.ndimage.grey_closing(combined, size=(PARAMS['morho']['big_kernel_size'],)*2)

print('thresholding')
thresh_high = (combined > (PARAMS['threshold']['high'] * 255)) * np.uint8(255)
# use a lower threshold to create the low confidence regions, so that they are larger
thresh_low = (combined > (PARAMS['threshold']['low'] * 255)) * np.uint8(255)

cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/og_segment_stuff/'+name_img+'high_og.jpg', thresh_high)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/og_segment_stuff/'+name_img+'low_og.jpg', thresh_low)



# noise removal
print('performing morphological operations and hole filling')
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

cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_original_segment_high_.JPG', high)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/'+name_img+'_original_segment_low_.JPG', low)

# save the resulting masks to files
print('writing resulting masks to output files')
export_results(high, args.out_high)
export_results(low, args.out_low)


print("My program took", time.time() - start_time, "to run")
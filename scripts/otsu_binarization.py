#!/usr/bin/env python3
import argparse
from pathlib import Path
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import scipy.ndimage
import time
start_time = time.time()
# from segment import export_results
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
    "out", help="the path to a file in which to store the json results"
)
args = parser.parse_args()



img = cv.imread(args.image)

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
print(str(args.image))

img_name = str(args.image).split("/")[-1]
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segment_trash/GRAY'+img_name, gray)

blur = cv.GaussianBlur(gray,(51,51),0)
ret3,th3 = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)

th3 = cv.bitwise_not(th3)
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segment_trash/'+img_name, th3)

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
        'block_size': 2001,
        'C': 10,
    },
    # Tom's addition:
    'num_of_features': {
        'high': 5,
        'low': 4
    },
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

small_kernel = np.ones((PARAMS['morho']['small_kernel_size'],)*2, np.uint8)
big_kernel = np.ones((PARAMS['morho']['big_kernel_size'],)*2, np.uint8)


# Now, we do morpho operations and hole filling to get the high confidence regions:
# 1) use the fill_holes method to boost background pixels that are surrounded by foreground
filled = scipy.ndimage.binary_fill_holes(th3) * np.uint8(255)
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

cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segment_trash/MORPH'+img_name, high)

# save the resulting masks to files
print('writing resulting masks to output files')
export_results(high, args.out)
print("My program took", time.time() - start_time, "to run")
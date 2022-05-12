#!/usr/bin/env python3
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Run the watershed algorithm to produce segmented regions in an orthomosaic. Or run watershed with multiple overlapping segmented regions."
)
parser.add_argument(
    "img", help="the path to the image"
)
parser.add_argument(
    "high", help="the path to the file that contain the coordinates of each extracted high confidence object (or a directory if there are multiple such files)"
)
parser.add_argument(
    "low", help="the path to the file that contain the coordinates of each extracted low confidence object (or a directory if there are multiple such files)"
)
parser.add_argument(
    "out", help="the path to the final segmented regions produced by running the watershed algorithm"
)
args = parser.parse_args()

import json
import os
import cv2 as cv
import numpy as np
import scipy.ndimage
import import_labelme
from imantics import Polygons

def import_segments(file, img_shape, pts=True):
    """
        import the segments in whatever format they're in as a bool mask
        provide img_shape if you want to ignore the coordinates of segments that lie outside of the img
    """
    # if the data is from labelme, import it using the labelme importer
    if file.endswith('.json'):
        labels = import_labelme.main(file, True, img_shape)
        label_keys = sorted(labels.keys())
        # make sure the segments are in sorted order, according to the keys
        labels = Polygons([labels[i] for i in label_keys])
        if pts:
            pts = {
                label_keys[i] : tuple(np.around(labels.points[i].mean(axis=0)).astype(np.uint))[::-1]
                for i in range(len(labels.points))
            }
        segments = labels.mask(*img_shape).array
    elif file.endswith('.npy'):
        segments = np.load(file) != 0
        if pts:
            # todo: implement pts here
            pts = {}
    else:
        raise Exception('Unsupported input file format.')
    return (pts, segments) if type(pts) is dict else segments

#def load_segments(high, low, high_all=None, low_all=None, img_shape=cv.imread(args.ortho)[:2]):
def load_segments(high, low, high_all=None, low_all=None, img_shape=None):
    """ load the segments and merge them with a cumulative OR of the segments """
    # first, load the segments as boolean masks
    pts, high_segs = import_segments(high, img_shape[::-1])
    low_segs = import_segments(low, img_shape[::-1], False)
    # create the high and low cumulative arrays if they don't exist yet
    if high_all is None:
        high_all = np.zeros(img_shape, dtype=np.uint8)
    if low_all is None:
        low_all = np.zeros(img_shape, dtype=np.uint8)
    # now merge the segments with the cumulative high and low masks
    return pts, np.add(high_all, high_segs), np.add(low_all, low_segs)

def largest_polygon(polygons):
    """ get the largest polygon among the polygons """
    # we should probably use a complicated formula to do this
    # but for now, it probably suffices to notice that the last one is usually
    # the largest
    return polygons.points[-1]


def export_results(ret, markers, out):
    """ write the resulting mask to a file """
    # should we save the segments as a mask or as bounding boxes?
    if out.endswith('.npy'):
        np.save(out, markers)
    elif out.endswith('.json'):
        # import extra required modules
        from imantics import Mask
        import import_labelme
        segments = [
            (int(i), largest_polygon(Mask(markers == i).polygons()).tolist())
            for i in (range(1, ret) if ret is not None else np.unique(markers).astype(int))
        ]
        import_labelme.write(out, segments, args.img)
    else:
        raise Exception("Unsupported output file format.")

img = cv.imread(args.img)
print("AHH")
high, low = None, None

_, high, low = load_segments(str(args.high), str(args.low), high, low, img.shape[:2])
# high = high.astype(np.float32)
# low = np.uint8(low != 0)

unknown = cv.subtract(low, high)

ret, markers = cv.connectedComponents(high)

# Add one to all labels so that sure background is not 0, but 1
markers = markers+1
# Now, mark the region of unknown with zero
markers[unknown==1] = 0

print('running the watershed algorithm')
markers = cv.watershed(img[:,:,0:3],markers)
print('finished watershed')

# clean up the indices
# merge background with old background
markers[markers == -1] = 1
markers -= 1

print('writing to desired output files')
# export_results(ret, markers, args.out)

label_hue = np.uint8(179*markers/1)
uniq_thresh = np.unique(label_hue).tolist()
cv.imwrite('/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/watershed_trial_2.jpg', label_hue)
uniq_thresh.sort(reverse=True)
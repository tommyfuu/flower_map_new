#!/usr/bin/env python3
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Use AP metrics to evaluate the segmentation performance of a selected directory."
)
parser.add_argument(
    "json", type=Path, help="the path to the folder that contain the coordinates of each extracted object for each image"
)
parser.add_argument(
    "gt", type=Path, help="the path to the folder/file that contain the coordinates of each ground truth object for each image"
)
parser.add_argument(
    "images", type=Path, help="the path to the folder that contain the images matching the annotation json files"
)
parser.add_argument(
    "out", help="the path to the file containing AP segmentation evaluation performance"
)
args = parser.parse_args()

import json
from glob import glob
from datetime import datetime,date
import cv2

# note that the feature based method is species-blind, 
# so no need for two different species categories
current_time = str(date.today().year)+"/"+str(date.today().month)+"/"+str(date.today().day)
preds_coco_dict = {
    'info': {
        'contributor': 'Tom Fu',
        'date_created': current_time,
        'description': 'prediction coco format dictionary',
        'url': 'null',
        'version': '1.0',
        'year': date.today().year
    },
    'annotations':[] ,
    'images': [],
    'licenses': [{'id': 1,
                'name': 'Attribution-NonCommercial License',
                'url': 'http://creativecommons.org/licenses/by-nc/2.0/'}],
    'categories': [{'id': 1, 'name': 'any', 'supercategory': 'any'}],
    # 'categories': [{'id': 1, 'name': 'SAAS', 'supercategory': 'SAAS'}, 
    #                 {'id': 2, 'name': 'ERFA', 'supercategory': 'ERFA'}]
}

gt_coco_dict = {
    'info': {
        'contributor': 'Tom Fu',
        'date_created': current_time,
        'description': 'gt coco format dictionary',
        'url': 'null',
        'version': '1.0',
        'year': date.today().year

    },
    'annotations':[] ,
    'images': [],
    'licenses': [{'id': 1,
                'name': 'Attribution-NonCommercial License',
                'url': 'http://creativecommons.org/licenses/by-nc/2.0/'}],
    'categories': [{'id': 1, 'name': 'any', 'supercategory': 'any'}],
    # 'categories': [{'id': 1, 'name': 'SAAS', 'supercategory': 'SAAS'}, 
    #                 {'id': 2, 'name': 'ERFA', 'supercategory': 'ERFA'}]
}

def PolyArea(x,y):
    "source: https://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates"
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

preds_segment_id = 1
gt_segment_id = 1

print("aaaa")
print("args.json")
print(args.json)
print(str(args.json) + '/*.json')
for idx, current_json_name in enumerate(glob(str(args.json) + '/*.json')):
    current_image_name = current_json_name.split('/')[-1].split(".")[-2]+'.JPG'
    print(current_image_name)
    current_image_path = str(args.images) + "/" + current_image_name
    print(current_image_path)
    current_groundtruth_name = str(args.gt) + "/" + current_json_name.split('/')[-1]
    print(current_groundtruth_name)
    if Path(current_json_name).is_file() and Path(current_groundtruth_name).is_file():
        with open(current_json_name) as f:
            preds_anns = json.load(f)
        with open(current_groundtruth_name) as f:
            gt_anns = json.load(f)
        
        print("trying")
        # add images to the dicts
        height, width = cv2.imread(current_image_path).shape[:2]
        current_image_dict = {'file_name': current_image_name,
                'height': height,
                'width': width,
                'id': current_image_name,
                'license': 1
                }
        if current_image_name not in preds_coco_dict:
            preds_coco_dict['images'].append(current_image_dict)
        if current_image_name not in gt_coco_dict:
            gt_coco_dict['images'].append(current_image_dict)

        # adjust format for preds from watershed
        for segment in preds_anns['shapes']:
            segment = segment["points"]
            current_preds_segment = [[item for sublist in segment for item in sublist]]
            current_preds_xs = [item[0] for item in segment]
            current_preds_ys = [item[1] for item in segment]
            print("???", max(current_preds_xs))
            # current_preds_segment_area = PolyArea(current_preds_xs, current_preds_ys)
            current_preds_bbox = [min(current_preds_xs), min(current_preds_ys),
             max(current_preds_xs)-min(current_preds_xs), max(current_preds_ys)-min(current_preds_ys)]
            current_preds_image_id = current_image_name

            current_segment_dict = {
                # 'area': current_preds_segment_area,
                'bbox': current_preds_bbox,
                'category_id': 1,
                'image_id': current_image_name,
                'id': preds_segment_id,
                'segmentation': current_preds_segment
            }

            preds_segment_id+=1

            # append
            preds_coco_dict['annotations'].append(current_segment_dict)

        # adjust format for gt
        for segment in gt_anns['labels']:
            current_gt_segment = [segment["segment"]]
            # current_gt_xs = [item[0] for item in segment]
            # current_gt_ys = [item[1] for item in segment]
            # current_gt_segment_area = PolyArea(current_gt_xs, current_gt_ys)
            current_gt_bbox = [segment["bbox_x"], segment["bbox_y"], segment["bbox_x"] + segment["width"], segment["bbox_y"] + segment["height"]],
            current_gt_image_id = current_image_name

            current_segment_dict = {
                # 'area': current_gt_segment_area,
                'bbox': current_gt_bbox,
                'category_id': 1,
                'id': gt_segment_id,
                'image_id': current_image_name,
                'segmentation': current_gt_segment
            }

            gt_segment_id+=1

            # append
            gt_coco_dict['annotations'].append(current_segment_dict)

out_file = open(str(args.out)+'_gt.json', "w")
json.dump(gt_coco_dict, out_file, indent = 6)
out_file = open(str(args.out)+'_preds.json', "w")
json.dump(preds_coco_dict, out_file, indent = 6)



# results = []
# for image_id in image_ids:
#     # Loop through detections
#     for i in range(rois.shape[0]):
#         class_id = class_ids[i]
#         score = scores[i]
#         bbox = np.around(rois[i], 1)
#         mask = masks[:, :, i]

#         result = {
#             "image_id": image_id,
#             "category_id": dataset.get_source_class_id(class_id, "coco"),
#             "bbox": [bbox[1], bbox[0], bbox[3] - bbox[1], bbox[2] - bbox[0]],
#             "score": score,
#             "segmentation": maskUtils.encode(np.asfortranarray(mask))
#         }
#         results.append(result)
# return results
# example_image = {u'coco_url': u'http://images.cocodataset.org/val2017/000000397133.jpg',
#  u'date_captured': u'2013-11-14 17:02:52',
#  u'file_name': u'000000397133.jpg',
#  u'flickr_url': u'http://farm7.staticflickr.com/6116/6255196340_da26cf2c9e_z.jpg',
#  u'height': 427,
#  u'id': 397133,
#  u'license': 4,
#  u'width': 640}


# example_annotation = {u'area': 1481.3806499999994,
#  u'bbox': [217.62, 240.54, 38.99, 57.75],
#  u'category_id': 44,
#  u'id': 82445,
#  u'image_id': 397133,
#  u'iscrowd': 0,
#  u'segmentation': [[224.24,
#    297.18,
#    228.29,
#    297.18,
#    234.91,
#    298.29,
#    243.0,
#    297.55,
#    249.25,
#    296.45,
#    252.19,
#    294.98,
#    256.61,
#    292.4,
#    254.4,
#    264.08,
#    251.83,
#    262.61,
#    241.53,
#    260.04,
#    235.27,
#    259.67,
#    230.49,
#    259.67,
#    233.44,
#    255.25,
#    237.48,
#    250.47,
#    237.85,
#    243.85,
#    237.11,
#    240.54,
#    234.17,
#    242.01,
#    228.65,
#    249.37,
#    224.24,
#    255.62,
#    220.93,
#    262.61,
#    218.36,
#    267.39,
#    217.62,
#    268.5,
#    218.72,
#    295.71,
#    225.34,
#    297.55]]}
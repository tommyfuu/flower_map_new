#!/usr/bin/env python3
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Use AP metrics to evaluate the segmentation performance of a selected directory."
)
parser.add_argument(
    "eval", default = 'both' ,help="either 'bbox' or 'segm' or 'both', representing the type of image-based evaluation being carried out."
)
parser.add_argument(
    "json", type=Path, help="the path to the folder that contain the coordinates of each extracted object for each image."
)
parser.add_argument(
    "gt", type=Path, help="the path to the folder/file that contain the coordinates of each ground truth object for each image"
)
parser.add_argument(
    "images", type=Path, help="the path to the folder that contain the images matching the annotation json files"
)
parser.add_argument(
    "out", help="the path to the file containing the json files generated to match the formats of preds and ground truth, as well as the output stats file"
)
parser.add_argument(
    "image_format", default = '.JPG', help="format of the images if not .JPG"
)
args = parser.parse_args()

import json
from glob import glob
from datetime import datetime,date
import cv2
import numpy as np 

# test cases: fail before computation
current_eval_type = str(args.eval)
if current_eval_type not in ['bbox', 'segm', 'both']:
    raise Exception('Please ensure that your eval type is \'bbox\' or \'segm\' or \'both\'.')


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

for idx, current_json_name in enumerate(glob(str(args.json) + '/*.json')):
    current_image_name = current_json_name.split('/')[-1].split(".")[-2]+str(args.image_format)
    current_image_path = str(args.images) + "/" + current_image_name
    current_groundtruth_name = str(args.gt) + "/" + current_json_name.split('/')[-1]
    if Path(current_json_name).is_file() and Path(current_groundtruth_name).is_file():
        with open(current_json_name) as f:
            preds_anns = json.load(f)
        
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

        # adjust format for preds from watershed
        for segment in preds_anns['shapes']:
            segment = segment["points"]
            current_preds_segment = [[item for sublist in segment for item in sublist]]
            current_preds_xs = [item[0] for item in segment]
            current_preds_ys = [item[1] for item in segment]
            current_preds_segment_area = PolyArea(current_preds_xs, current_preds_ys)
            current_preds_bbox = [min(current_preds_xs), min(current_preds_ys),
             max(current_preds_xs)-min(current_preds_xs), max(current_preds_ys)-min(current_preds_ys)]
            current_preds_image_id = current_image_name

            current_segment_dict = {
                'area': current_preds_segment_area,
                'bbox': current_preds_bbox,
                'category_id': 1,
                'image_id': current_image_name,
                'id': preds_segment_id,
                'segmentation': current_preds_segment,
                'iscrowd': 0,
                'score': 0.5 # TODO: potential changes
            }

            preds_segment_id+=1

            # append
            preds_coco_dict['annotations'].append(current_segment_dict)

    if Path(current_groundtruth_name).is_file():
        with open(current_groundtruth_name) as f:
            gt_anns = json.load(f)

        # add images to the dicts
        height, width = cv2.imread(current_image_path).shape[:2]
        current_image_dict = {'file_name': current_image_name,
                'height': height,
                'width': width,
                'id': current_image_name,
                'license': 1
                }
        if current_image_name not in gt_coco_dict:
            gt_coco_dict['images'].append(current_image_dict)

        # adjust format for gt
        for segment in gt_anns['labels']:
            current_gt_segment = segment["segment"]
            current_gt_xs = [item for index, item in enumerate(current_gt_segment) if index%2==0]
            current_gt_ys = [item for index, item in enumerate(current_gt_segment) if index%2==1]
            print("current_gt_xs", current_gt_xs)
            print("current_gt_ys", current_gt_ys)
            current_gt_segment_area = PolyArea(current_gt_xs, current_gt_ys)
            current_gt_bbox = [segment["bbox_x"], segment["bbox_y"], segment["bbox_x"] + segment["width"], segment["bbox_y"] + segment["height"]],
            current_gt_image_id = current_image_name
            

            print("AAAAA", current_gt_segment)
            current_segment_dict = {
                'area': current_gt_segment_area,
                'bbox': current_gt_bbox[0],
                'category_id': 1,
                'id': gt_segment_id,
                'image_id': current_image_name,
                'segmentation': [current_gt_segment],
                'iscrowd': 0,
            }

            gt_segment_id+=1

            # append
            gt_coco_dict['annotations'].append(current_segment_dict)



gtFile = open(str(args.out)+'_gt.json', "w")
json.dump(gt_coco_dict, gtFile, indent = 6)
predsFile = open(str(args.out)+'_preds.json', "w")
json.dump(preds_coco_dict, predsFile, indent = 6)

from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

# conduct evaluation
def eval_coco(annType, gtFile, predsFile, current_stats_file):
    cocoGt = COCO(gtFile)
    cocoDt = COCO(predsFile)
    cocoEval = COCOeval(cocoGt,cocoDt,annType)
    cocoEval.evaluate()
    cocoEval.accumulate()
    cocoEval.summarize()
    current_stats = list(cocoEval.stats)
    current_stat_text = '\n' + 'evaluation stats - type '+annType + '\n'
    current_stat_text += current_time + '\n'
    current_stat_text += 'ground truth source:' + str(args.gt) + '/*.json' + '\n'
    current_stat_text += 'prediction result source:' + str(args.json) + '/*.json' + '\n'
    current_stat_text += 'image source:' + str(args.images) + '\n'
    current_stat_text += ' Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = ' + current_stats[0] + '\n'
    current_stat_text += ' Average Precision  (AP) @[ IoU=0.50      | area=   all | maxDets=100 ] = ' + current_stats[1] + '\n'
    current_stat_text += ' Average Precision  (AP) @[ IoU=0.75      | area=   all | maxDets=100 ] = ' + current_stats[2] + '\n'
    current_stat_text += ' Average Precision  (AP) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = ' + current_stats[3] + '\n'
    current_stat_text += ' Average Precision  (AP) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = ' + current_stats[4] + '\n'
    current_stat_text += ' Average Precision  (AP) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = ' + current_stats[5] + '\n'
    current_stat_text += ' Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=  1 ] = ' + current_stats[6] + '\n'
    current_stat_text += ' Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets= 10 ] = ' + current_stats[7] + '\n'
    current_stat_text += ' Average Recall     (AR) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = ' + current_stats[8] + '\n'
    current_stat_text += ' Average Recall     (AR) @[ IoU=0.50:0.95 | area= small | maxDets=100 ] = ' + current_stats[9] + '\n'
    current_stat_text += ' Average Recall     (AR) @[ IoU=0.50:0.95 | area=medium | maxDets=100 ] = ' + current_stats[10] + '\n'
    current_stat_text += ' Average Recall     (AR) @[ IoU=0.50:0.95 | area= large | maxDets=100 ] = ' + current_stats[11] + '\n'
    

    with open(current_stats_file, 'a') as f:
        f.write(current_stat_text)
    return

current_stats_file = str(args.out)+'_eval_stats.txt'
if current_eval_type in ['segm','bbox']:
    eval_coco(current_eval_type, gtFile, predsFile, current_stats_file)
elif current_eval_type == 'both':
    eval_coco('bbox', gtFile, predsFile, current_stats_file)
    eval_coco('segm', gtFile, predsFile, current_stats_file)
print("evaluation done.")
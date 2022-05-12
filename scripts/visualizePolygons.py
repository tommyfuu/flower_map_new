#!/usr/bin/env python3
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import json
import os
import cv2  # python-opencv
import numpy as np
import time

parser = argparse.ArgumentParser(
    description=
    """
        Visualize the polygons in a json file and generate the associated json file for that.
    """
)
parser.add_argument(
    "dataDir", help="a path to the image directory"
)
parser.add_argument(
    "img_postfix", help="the postfix of the image files, example: '.JPG'"
)
parser.add_argument(
    "annFile", help="path to the annotation file"
)
parser.add_argument(
    "endDir", help="path to the ending image directory (where the files will end up at)"
)
parser.add_argument(
    "jsonDir", help="path to the ending json directory (where the files will end up at)"
)
parser.add_argument(
    "option", help="the option to run: 'visualize' or 'generate' or 'both" 
)
args = parser.parse_args()

dataDir = args.dataDir
img_postfix = args.img_postfix
annFile = args.annFile  
endDir = args.endDir
jsonDir = args.jsonDir

## aim
# visualize datasets of images with their annotations
# generate individual json files usable for training mask r-cnn models

OPTION = args.option # either visualize or json


# Opening JSON file
f = open(annFile)

# returns JSON object as
# a dictionary
data = json.load(f)

classes = {}

class_counter = 0
for class_l in data['categories']['label']['labels']:
    if class_l['name'] not in classes.values():
        classes.update({class_counter: class_l['name']})
        class_counter+=1

print(classes)
if OPTION == 'visualize' or 'BOTH':

    isClosed = True
    colors = [(255, 0, 0), (0, 255, 0)]

    print("AAAAAA", len(data['items']))
    for image in data['items']:
        image_id = image['id']
        image_path = dataDir+'/'+image_id+img_postfix
        print(image_path)
        image_cv2 = cv2.imread(image_path)
        
        try:
            test = image_cv2.any()
            if not os.path.isfile(endDir+"/ANNOTATED_"+image_id+'.JPG'):
                for annotation in image['annotations']:
                    current_class = classes[annotation['id']]
                    current_polygon = np.array(annotation['points'])
                    current_polygon_2d = np.reshape(current_polygon, (int(len(current_polygon)/2),2))

                    # print(current_polygon_2d)
                    current_polygon_2d = current_polygon_2d.reshape((-1, 1, 2))

                    current_species = np.array(annotation['label_id']) # species = 1 buckwheats, species = 2 whitesages
                    line_thickness = 2
                    cv2.polylines(image_cv2, np.int32([current_polygon_2d]), isClosed, colors[current_species], thickness=line_thickness)

                # cv2.imshow("image.jpg", image_cv2)
                print("ANNOTATED_"+image_id+'.JPG')
                cv2.imwrite(endDir+"/ANNOTATED_"+image_id+'.JPG', image_cv2)
            else:
                print("Already exist: ANNOTATED_"+image_id+'.JPG')
        except:
            print("ERROR_"+image_id+'.JPG')
            with open(endDir+'errorLog.txt', 'a') as the_file:
                the_file.write(str(image)+'\n\n')
        
elif OPTION == 'json' or 'BOTH':
    current_label_id = 0
    for image in data['items']:
        image_id = image['id']
        image_path = dataDir+'/'+image_id+img_postfix
        print(image_path)
        # initialize stuff for current image json dict
        current_image_classes = []
        current_plant_number = 0
        current_labels = []
        if not os.path.isfile(jsonDir+'/'+image_id+'.json'):
            for annotation in image['annotations']:
                # fetch info
                current_class = classes[annotation['label_id']]
                print(annotation['label_id'], current_class)

                current_polygon = np.array(annotation['points'])
                current_polygon_2d = np.reshape(current_polygon, (int(len(current_polygon)/2),2))
                current_polygon_2d = np.transpose(current_polygon_2d)
                current_species = np.array(annotation['label_id']) # species = 1 buckwheats, species = 2 whitesages
                print("Current species", current_species)
                # update stuff for the current image json dict
                if current_class not in current_image_classes:
                    current_image_classes.append(current_class)
                current_plant_number += 1
                current_label_id += 1
                current_labels.append({
                    "class": current_class,
                    "id": current_label_id,
                    "bbox_x": min(current_polygon_2d[0]),
                    "width": max(current_polygon_2d[0])-min(current_polygon_2d[0]),
                    "bbox_y": min(current_polygon_2d[1]),
                    "height": max(current_polygon_2d[1])-min(current_polygon_2d[1]),
                    "segment": list(current_polygon),
                    
                })

        # generate a dict
        current_img_dict = {
            "classes": current_image_classes,
            "number_of_plants": current_plant_number,
            "labels": current_labels,
            "sample_id": image_id
        }
        # get dict into a json file
        out_file = open(jsonDir+'/'+image_id+'.json', "w")

        json.dump(current_img_dict, out_file, indent = 6)
        print('json generated')

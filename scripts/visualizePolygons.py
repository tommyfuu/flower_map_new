import matplotlib.pyplot as plt
import json
import os
import cv2  # python-opencv
import numpy as np
import time


# # test set 1
# dataDir = '/mnt/biology/donaldson/tom/flower_map/data/Week3/6217East'
# img_postfix = '.JPG'
# annFile='/mnt/biology/donaldson/tom/flower_map_new/annotations/2017_6217east.json'
# endDir = '/mnt/biology/donaldson/tom/flower_map_new/annotations/20176217east_annotated'

# test set 2
# dataDir = '/mnt/biology/donaldson/tom/flower_map/data/Week4/6617East2'
# img_postfix = '.JPG'
# annFile='/mnt/biology/donaldson/tom/flower_map_new/annotations/2017_6617east2.json'
# endDir = '/mnt/biology/donaldson/tom/flower_map_new/annotations/20176617east2_annotated'

# test set 3
# dataDir = '/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North'
# img_postfix = '.JPG'
# annFile = '/mnt/biology/donaldson/tom/flower_map_new/annotations/070921_north.json'
# endDir = '/mnt/biology/donaldson/tom/flower_map_new/annotations/20210709north_annotated'

# test set 4
dataDir = '/mnt/biology/donaldson/tom/flower_map_new/newData/071121_CentralEastern'
img_postfix = '.JPG'
annFile = '/mnt/biology/donaldson/tom/flower_map_new/annotations/071121_centraleastern.json'
endDir = '/mnt/biology/donaldson/tom/flower_map_new/annotations/20210711centralEastern_annotated'

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

isClosed = True
colors = [(255, 0, 0), (0, 255, 0)]

print("AAAAAA", len(data['items']))
for image in data['items']:
    image_id = image['id']
    image_path = dataDir+'/'+image_id+img_postfix
    print(image_path)
    image_cv2 = cv2.imread(image_path)
    
    if image_cv2.any():
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
        print("ERROR_"+image_id+'.JPG')
        with open(endDir+'errorLog.txt', 'a') as the_file:
            the_file.write(image+'\n\n')
        








# coco=COCO(annFile)
# annFile = '{}/annotations/person_keypoints_{}.json'.format(dataDir,dataType)
# coco_kps=COCO(annFile)


# catIds = coco.getCatIds(catNms=['person'])
# imgIds = coco.getImgIds(catIds=catIds );
# imgIds = coco.getImgIds(imgIds = imgIds[0])
# img = coco.loadImgs(imgIds[np.random.randint(0,len(imgIds))])[0]
# I = io.imread(dataDir+'/images/default/'+img['file_name'])

# plt.imshow(I); plt.axis('off')
# annIds = coco.getAnnIds(imgIds=img['id'], catIds=catIds, iscrowd=None)
# anns = coco.loadAnns(annIds)
# coco.showAnns(anns)


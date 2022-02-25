import json
import os
import glob

ANNOTATION_PATH = '/mnt/biology/donaldson/tom/flower_map_new/annotations'

total_num_of_polygons = 0
total_num_of_images = 0
for file_name in glob.glob(ANNOTATION_PATH+'/*'):
    if file_name[-4:] == 'json':
        # Opening JSON file
        f = open(file_name)
        print("current dataset", file_name)
        # returns JSON object as
        # a dictionary
        data = json.load(f)
        current_num_of_polygons = 0
        current_num_of_images = 0
        for image in data['items']:
            current_num_of_images+=1
            image_id = image['id']
            
            for annotation in image['annotations']:
                current_num_of_polygons+=1
                # print("current_num_of_polygons", current_num_of_polygons)
            
        print("current_num_of_images", current_num_of_images)
        print("current_num_of_polygons", current_num_of_polygons)
        total_num_of_images+=current_num_of_images
        total_num_of_polygons+=current_num_of_polygons

print("final_count")
print("total_num_of_images", total_num_of_images)
print("total_num_of_polygons", total_num_of_polygons)

# total_num_of_images 1120
# total_num_of_polygons 13445

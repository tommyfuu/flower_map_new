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
        class_counter = 0
        classes = {}
        for class_l in data['categories']['label']['labels']:
            if class_l['name'] not in classes.values():
                classes.update({class_counter: class_l['name']})
                class_counter+=1
        print(classes)
        current_num_of_polygons = 0
        current_num_of_images = 0
        current_num_of_buckwheats = 0
        current_num_of_white_sages = 0
        for image in data['items']:
            current_num_of_images+=1
            image_id = image['id']
            
            for annotation in image['annotations']:
                current_num_of_polygons+=1
                # print("current species", annotation['label_id'])
                # print(classes[annotation['label_id']])
                if annotation['label_id'] in classes.keys() and classes[annotation['label_id']] == 'ERFA':
                    current_num_of_buckwheats += 1
                if annotation['label_id'] in classes.keys() and classes[annotation['label_id']] == 'SAAP':
                    current_num_of_white_sages += 1
                # print("current_num_of_polygons", current_num_of_polygons)
            
        print("current_num_of_images", current_num_of_images)
        print("current_num_of_polygons", current_num_of_polygons)
        print("current_num_of_buckwheats", current_num_of_buckwheats)
        print("current_num_of_white_sages", current_num_of_white_sages)
        total_num_of_images+=current_num_of_images
        total_num_of_polygons+=current_num_of_polygons

print("final_count")
print("total_num_of_images", total_num_of_images)
print("total_num_of_polygons", total_num_of_polygons)

# total_num_of_images 1120
# total_num_of_polygons 13445

#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd
from subprocess import Popen, PIPE
# find_images('/mnt/biology/donaldson/tom/flower_map_new/2017_6217East.csv',
#         '/mnt/biology/donaldson/tom/flower_map/data/Week3/6217East',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6217East_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/2017_6217East"')


# upload_jsons('/mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20176217_east', 
#             '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/2017_6217East"')

parser = argparse.ArgumentParser(
    description="find images and upload to google drive")
)
parser.add_argument(
    "image_range", help="path to the csv file defining the range of images to be uploaded. example seen at /mnt/biology/donaldson/tom/flower_map_new/2017_6217East.csv.")
)
parser.add_argument(
    "image_dir", help="path to the directory of images to be selected from. example seen at /mnt/biology/donaldson/tom/flower_map/data/Week3/6217East.")
)
parser.add_argument(
    "output_txt_path", help="path to the file you want to include all the names of the files you are uploading. example seen at '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6217East_summary.txt'.")
)
parser.add_argument(
    "jsons_path", help="path to the json files to be uploaded. example seen at: /mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20176217_east.")
)
parser.add_argument(
    "gdrive_path", help="path to upload the files to.")
)
args = parser.parse_args()

def find_images(csv_summary_path, directory_path, output_txt_path, gDrive_path):
    a = pd.read_csv(csv_summary_path)
    start_list = a['image_name_start'].tolist()
    end_list = a['image_name_end'].tolist()
    all_contained_image_names = []
    print("prep start, identifying all images")
    for index in range(len(start_list)):
        current_start = start_list[index]
        current_end = end_list[index]

        current_prefix = ""
        current_prefix_list = current_start.split("_")[:-1]
        for el in current_prefix_list:
            current_prefix += el + "_"
        
        current_start_number = int(current_start.split("_")[-1])
        current_end_number = int(current_end.split("_")[-1])
        current_range = range(current_start_number, current_end_number)
        
        current_range_image_names = []
        for image in current_range:
            if len(str(image)) == 2:
                current_range_image_names.append(current_prefix+'00'+str(image)+".JPG")
            elif len(str(image)) == 3:
                current_range_image_names.append(current_prefix+'0'+str(image)+".JPG")
            elif len(str(image)) == 1:
                current_range_image_names.append(current_prefix+'000'+str(image)+".JPG")
        all_contained_image_names.extend(current_range_image_names)
    print("writing image names to txt file at", output_txt_path)
    with open(output_txt_path, 'w') as f:
        for item in all_contained_image_names:
            f.write("%s\n" % item)
    
    include_from = '--include-from='+output_txt_path
    
    process = 'rclone copy '+directory_path+" "+gDrive_path+" "+include_from +" -v"
    print("prep finished, run the following command to upload all chosen images")
    print(process)
    # process = Popen(['rclone', 'copy', directory_path, gDrive_path, include_from, '-v'], stdout=PIPE, stderr=PIPE)
    # stdout, stderr = process.communicate()
    return all_contained_image_names



# find_images('/mnt/biology/donaldson/tom/flower_map_new/070921_NorthHasPlants.csv',
#         '/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/0709_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/070921_North"')

# find_images('/mnt/biology/donaldson/tom/flower_map_new/071121_CentralEasternHasPlants.csv',
#         '/mnt/biology/donaldson/tom/flower_map_new/newData/071121_CentralEastern',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/0711_CentralEastern_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/071121_CentralEastern"')

# find_images('/mnt/biology/donaldson/tom/flower_map_new/071621_South.csv',
#         '/mnt/biology/donaldson/tom/flower_map_new/newData/071621_South',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/071621_South_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/071621_South"')


# find_images('/mnt/biology/donaldson/tom/flower_map_new/071121_Western.csv',
#         '/mnt/biology/donaldson/tom/flower_map_new/newData/071121_Western',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/071121_Western_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/071121_Western"')

# find_images('/mnt/biology/donaldson/tom/flower_map_new/2017_6217East.csv',
#         '/mnt/biology/donaldson/tom/flower_map/data/Week3/6217East',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6217East_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/2017_6217East"')

# find_images('/mnt/biology/donaldson/tom/flower_map_new/2017_6617East1.csv',
#         '/mnt/biology/donaldson/tom/flower_map/data/Week4/6617East1',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6617East1_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/2017_6617East1"')

# find_images('/mnt/biology/donaldson/tom/flower_map_new/2017_6617East2.csv',
#         '/mnt/biology/donaldson/tom/flower_map/data/Week4/6617East2',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6617East2_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/2017_6617East2"')

# find_images('/mnt/biology/donaldson/tom/flower_map_new/2017_6917West.csv',
#         '/mnt/biology/donaldson/tom/flower_map/data/Week4/6917West',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6917West_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/2017_6917West"')


def upload_jsons(json_folder, gDrive_path):
      
    process = 'rclone copy '+json_folder+" "+gDrive_path+" "+" -v"
    print("prep finished, run the following command to upload all chosen images")
    print(process)
    # process = Popen(['rclone', 'copy', directory_path, gDrive_path, include_from, '-v'], stdout=PIPE, stderr=PIPE)
    # stdout, stderr = process.communicate()
    return

# upload_jsons('/mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20176217_east', 
#             '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/2017_6217East_json"')

# find_images('/mnt/biology/donaldson/tom/flower_map_new/2017_6217East.csv',
#         '/mnt/biology/donaldson/tom/flower_map/data/Week3/6217East',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6217East_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/2017_6217East_json"')

# upload_jsons('/mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20176917_west', 
#             '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/2017_6917West_json"')

# find_images('/mnt/biology/donaldson/tom/flower_map_new/2017_6917West.csv',
#         '/mnt/biology/donaldson/tom/flower_map/data/Week4/6917West',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6917West_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/2017_6917West_json"')




#### Final Data Uploads

# find_images('/mnt/biology/donaldson/tom/flower_map_new/070921_NorthHasPlants.csv',
#         '/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/0709_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/070921_North"')

# upload_jsons('/mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20210709_north', 
#             '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/070921_North"')


# find_images('/mnt/biology/donaldson/tom/flower_map_new/071121_CentralEasternHasPlants.csv',
#         '/mnt/biology/donaldson/tom/flower_map_new/newData/071121_CentralEastern',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/0711_CentralEastern_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/071121_CentralEastern"')

# upload_jsons('/mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20210711_centralEastern', 
#             '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/071121_CentralEastern"')



# find_images('/mnt/biology/donaldson/tom/flower_map_new/071621_South.csv',
#         '/mnt/biology/donaldson/tom/flower_map_new/newData/071621_South',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/071621_South_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/071621_South"')

# upload_jsons('/mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20210716_south', 
#             '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/071621_South"')


# find_images('/mnt/biology/donaldson/tom/flower_map_new/071121_Western.csv',
#         '/mnt/biology/donaldson/tom/flower_map_new/newData/071121_Western',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/071121_Western_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/071121_Western"')

# upload_jsons('/mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20210711_western', 
#             '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/071121_Western"')

# find_images('/mnt/biology/donaldson/tom/flower_map_new/2017_6217East.csv',
#         '/mnt/biology/donaldson/tom/flower_map/data/Week3/6217East',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6217East_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/2017_6217East"')


# upload_jsons('/mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20176217_east', 
#             '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/2017_6217East"')

# find_images('/mnt/biology/donaldson/tom/flower_map_new/2017_6617East1.csv',
#         '/mnt/biology/donaldson/tom/flower_map/data/Week4/6617East1',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6617East1_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/2017_6617East1"')

# upload_jsons('/mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20176617_east1', 
#             '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/2017_6617East1"')

# find_images('/mnt/biology/donaldson/tom/flower_map_new/2017_6617East2.csv',
#         '/mnt/biology/donaldson/tom/flower_map/data/Week4/6617East2',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6617East2_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/2017_6617East2"')

# upload_jsons('/mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20176617_east2', 
#             '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/2017_6617East2"')


# find_images('/mnt/biology/donaldson/tom/flower_map_new/2017_6917West.csv',
#         '/mnt/biology/donaldson/tom/flower_map/data/Week4/6917West',
#         '/mnt/biology/donaldson/tom/flower_map_new/useful_images_summaries/2017_6917West_summary.txt',
#         '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/2017_6917West"')

# upload_jsons('/mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20176917_west', 
#             '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/labelled data/2017_6917West"')

if __name__ == "__main__":
    find_images(args.image_range, args.image_dir, args.output_txt_path, args.gdrive_path)
    upload_jsons(args.jsons_path, args.gdrive_path)
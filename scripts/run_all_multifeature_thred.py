#!/usr/bin/env python3
import argparse
import subprocess
import glob
import os.path
from pathlib import Path

parser = argparse.ArgumentParser(
    description=
    """
        run a segmentation process at scale
    """
)
parser.add_argument(
    "process_to_run", help="choose a process to run, options include 'watershed', 'multifeature', 'otsu', 'existing'. When typed, do not include quotation marks."
)
args = parser.parse_args()


# for file in glob.glob("/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/*.JPG"):
#     image_name = file.split("/")[-1].split(".")[0]
#     if "original_segment" in image_name:
#         os.remove(file)

print("when input paths for ")
if args.process_to_run == 'watershed':
    img_dir = input("Enter the path for image directory: ")
    high_dir = input("Enter the path for high confidence segment directory: ")
    low_dir = input("Enter the path for low confidence segment directory: ")
    out_dir = input("Enter the path for output directory including all watershed json files: ")
    
    for file in glob.glob(img_dir+"/*.JPG"):
        image_name = file.split("/")[-1].split(".")[0]
        if not os.path.isfile(out_dir+"/"+image_name+'.json'):
            print("filename", file)
            subprocess.call(["python3", "/mnt/biology/donaldson/tom/flower_map_new/scripts/watershed_single_image.py", 
            img_dir+"/"+image_name+".JPG", 
            low_dir+"/"+image_name+".json",
            high_dir+"/"+image_name+".json",
            out_dir+"/"+image_name+'.json'])

elif args.process_to_run == 'multifeature':
    img_dir = input("Enter the path for image directory: ")
    texture_cache = input("Enter the path for texture cache directory, if not exist, type NA: ")
    high_dir = input("Enter the path for high confidence segment directory: ")
    low_dir = input("Enter the path for low confidence segment directory: ")

    for file in glob.glob(img_dir+"/*.JPG"):
        image_name = file.split("/")[-1].split(".")[0]
        if not os.path.isfile(high_dir+"/"+image_name+'.json'):
            print("filename", file)
            if texture_cache != "NA":
                subprocess.call(["python3", "/mnt/biology/donaldson/tom/flower_map_new/scripts/multi_feature_segment.py", 
                "--texture-cache", texture_cache+"/"+image_name+".npy",
                img_dir+"/"+image_name+".JPG", 
                low_dir+"/"+image_name+".json",
                high_dir+"/"+image_name+".json"])
            else:
                subprocess.call(["python3", "/mnt/biology/donaldson/tom/flower_map_new/scripts/multi_feature_segment.py", 
                img_dir+"/"+image_name+".JPG", 
                low_dir+"/"+image_name+".json",
                high_dir+"/"+image_name+".json"])

elif args.process_to_run == 'existing':
    img_dir = input("Enter the path for image directory: ")
    texture_cache = input("Enter the path for texture cache directory, if not exist, type NA: ")
    high_dir = input("Enter the path for high confidence segment directory: ")
    low_dir = input("Enter the path for low confidence segment directory: ")

    for file in glob.glob(img_dir+"/*.JPG"):
        image_name = file.split("/")[-1].split(".")[0]
        if not os.path.isfile(high_dir+"/"+image_name+'.json'):
            print("filename", file)
            if texture_cache != "NA":
                subprocess.call(["python3", "/mnt/biology/donaldson/tom/flower_map_new/scripts/segment.py", 
                "--texture-cache", texture_cache+"/"+image_name+".npy",
                img_dir+"/"+image_name+".JPG", 
                low_dir+"/"+image_name+".json",
                high_dir+"/"+image_name+".json"])
            else:
                subprocess.call(["python3", "/mnt/biology/donaldson/tom/flower_map_new/scripts/segment.py", 
                img_dir+"/"+image_name+".JPG", 
                low_dir+"/"+image_name+".json",
                high_dir+"/"+image_name+".json"])

elif args.process_to_run == 'otsu':
    img_dir = input("Enter the path for image directory: ")
    out_dir = input("Enter the path for the directory storing output json files: ")
    Path(img_dir).mkdir(parents=True, exist_ok=True)
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    for file in glob.glob(img_dir+"/*.JPG"):
        image_name = file.split("/")[-1].split(".")[0]
        if not os.path.isfile(out_dir+"/"+image_name+'.json'):
            print("filename", file)
            subprocess.call(["python3", "/mnt/biology/donaldson/tom/flower_map_new/scripts/otsu_binarization.py", 
                img_dir+"/"+image_name+".JPG", 
                out_dir+"/"+image_name+".json"])
# for file in glob.glob("/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/*.JPG"):
#     image_name = file.split("/")[-1].split(".")[0]
#     # print("filename", file)
#     if not os.path.isfile('/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/existing_watershed/'+image_name+'.json'):
#         print("filename", file)
#         subprocess.call(["python3", "/mnt/biology/donaldson/tom/flower_map_new/scripts/watershed_single_image.py", 
#         "/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/"+image_name+".JPG", 
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/high/"+image_name+".json",
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/low/"+image_name+".json",
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/existing_watershed/"+image_name+".json"])



# for file in glob.glob("/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/*.JPG"):
#     image_name = file.split("/")[-1].split(".")[0]
#     # print("filename", file)
#     if not os.path.isfile('/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/multi_high/'+image_name+'.json'):
#         print("filename", file)
#         subprocess.call(["python3", "/mnt/biology/donaldson/tom/flower_map_new/scripts/multi_feature_segment.py", 
#         "--texture-cache", "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/texture/"+image_name+".npy",
#         "/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/"+image_name+".JPG", 
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/multi_high/"+image_name+".json", 
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/multi_low/"+image_name+".json"])

# for file in glob.glob("/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/*.JPG"):
#     image_name = file.split("/")[-1].split(".")[0]
#     # print("filename", file)
#     if not os.path.isfile('/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/otsu/'+image_name+'.json'):
#         print("filename", file)
#         subprocess.call(["python3", "/mnt/biology/donaldson/tom/flower_map_new/scripts/otsu_binarization.py", 
#         "/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/"+image_name+".JPG", 
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/otsu/"+image_name+".json"])


# for file in glob.glob("/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/*.JPG"):
#     image_name = file.split("/")[-1].split(".")[0]
#     if "original_segment" in image_name:
#         os.remove(file)

# for file in glob.glob("/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/*.JPG"):
#     image_name = file.split("/")[-1].split(".")[0]
#     # print("filename", file)
#     if not os.path.isfile('/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/multi_watershed/'+image_name+'.json'):
#         print("filename", file)
#         subprocess.call(["python3", "/mnt/biology/donaldson/tom/flower_map_new/scripts/watershed_single_image.py", 
#         "/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/"+image_name+".JPG", 
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/multi_high/"+image_name+".json",
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/multi_low/"+image_name+".json",
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/multi_watershed/"+image_name+".json"])

# for file in glob.glob("/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/*.JPG"):
#     image_name = file.split("/")[-1].split(".")[0]
#     # print("filename", file)
#     if not os.path.isfile('/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/existing_watershed/'+image_name+'.json'):
#         print("filename", file)
#         subprocess.call(["python3", "/mnt/biology/donaldson/tom/flower_map_new/scripts/watershed_single_image.py", 
#         "/mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/"+image_name+".JPG", 
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/high/"+image_name+".json",
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/low/"+image_name+".json",
#         "/mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/existing_watershed/"+image_name+".json"])


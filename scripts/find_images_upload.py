import pandas as pd
from subprocess import Popen, PIPE


def find_images(csv_summary_path, directory_path, output_txt_path, gDrive_path):
    a = pd.read_csv(csv_summary_path)
    start_list = a['image_name_start'].tolist()
    end_list = a['image_name_end'].tolist()
    all_contained_image_names = []
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
        # current_range_image_names = [current_prefix+'0'+str(image)+".JPG" for image in current_range]
        # current_range_image_names = [directory_path+"/"+current_prefix+str(image)+".JPG" for image in current_range]
        all_contained_image_names.extend(current_range_image_names)

    with open(output_txt_path, 'w') as f:
        for item in all_contained_image_names:
            print(item)
            f.write("%s\n" % item)
    
    include_from = '--include-from='+output_txt_path
    
    process = 'rclone copy '+directory_path+" "+gDrive_path+" "+include_from +" -v"
    print(process)
    # process = Popen(['rclone', 'copy', directory_path, gDrive_path, include_from], stdout=PIPE, stderr=PIPE)
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

find_images('/mnt/biology/donaldson/tom/flower_map_new/071621_South.csv',
        '/mnt/biology/donaldson/tom/flower_map_new/newData/071621_South',
        '/mnt/biology/donaldson/tom/flower_map_new/071621_South.csv',
        '"knuthXGDrive:/Bee Lab/Projects/Bee Forage Mapping/Bee Forage Mapping - Tom Thesis/dataToBeLabelled/071621_South"')

# TOM_SCRIPTS.md

## introduction
This is an instruction on how to run scripts updated in Tom's thesis (2021-2022). All the explanations on how to run the scripts are listed in alphabetical order in terms of script names.

It is important to note that a lot of these scripts might rely on dependencies in the snakemake conda environment. Rather than installing them by hand, I have created a yml file in the mother directory (`flower_map_new`) called `environment_tom_snakemake.yml`. To create a conda environment with all these dependencies, you can simply do:

```
conda env create -f environment_tom_snakemake.yml
```

It might take a while to run it because there are a lot of dependencies to install, but it should work eventually.

Make sure you activate the conda environment before you run the scripts.

## script manuals

### countAnnotations.py

This script enables a user to count how many annotations of each species there are in each of the annotation json file in the format shown in `/mnt/biology/donaldson/tom/flower_map_new/annotations/2017_6217east.json`. It takes as the input a directory containing all such annotation json files you are interested in.

To run the script, you can do, for example
```
python countAnnotations.py /mnt/biology/donaldson/tom/flower_map_new/annotations
```

### evaluate_segments.py

This script allows user to evaluate the segmentation performance of a method. It compares the image-level segmentation results from an existing method (at the end of watershed) with the given ground truth that's also on the image level.

```
python eval species json gt images out image_format
```

Example on how to run this script is below, if you want help on what each of the arguments above means, simply type `python evaluate_segments.py -h` in the terminal.

```
python evaluate_segments.py both both /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/multi_watershed /mnt/biology/donaldson/tom/flower_map_new/annotations/jsons_20210709_north /mnt/biology/donaldson/tom/flower_map_new/newData/070921_North /mnt/biology/donaldson/tom/flower_map_new/multi_trial_0 .JPG
```


### few_images_train.py
This script is part of the multi-feature voting segmentation scheme, the process for training a generalized linear model to get the weights for the features in the later segmentation process.

```
python few_images_train.py (--texture-cache TEXTURE_CACHE_DIRECTORY) cvat_path out
```

depending on whether you use the texture-cache (if you run the original pipeline, this texture cache should be available)

if you have the texture-cache
```
python few_image_train.py --texture-cache /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/texture /mnt/biology/donaldson/tom/flower_map_new/mini_trainset /mnt/biology/donaldson/tom/flower_map_new/out 
```

if you do NOT have the texture-cache
```
python few_image_train.py /mnt/biology/donaldson/tom/flower_map_new/mini_trainset /mnt/biology/donaldson/tom/flower_map_new/out 
```

### find_images_upload.py 

```
python find_images_upload.py
```

You should follow the instructions as they come up. For example: 


Note that after this is done without any issues, you will be given 2 resultant commands to run to actually upload all images to google drive using RClone, for example:

![RClone commands](https://github.com/tommyfuu/flower_map_new/blob/master/scripts/exp_pics/find_images_upload.png)

Running these commands will require RClone, which you can install by using the commands listed [here](https://anaconda.org/conda-forge/rclone).

RClone might require prior set up from command line, you can do that by typing in `rclone config` in terminal and finish setting it up in the way you desire. One example on setting it up can be found in [this document](https://docs.google.com/document/d/1eikj_XFX3dv1gD2FTH-xkE46AWknP0QViZqG6N8WmZ0/edit#bookmark=id.wrkoufkfttnc) (If you are a bee lab member, you should have access to this document.) 

### multi_feature_segment.py

A script to be run on one image at a time to conduct multi-feature thresholding. To run this at scale, please check out [run_all_multifeature_thred.py](#runallmultifeaturethredpy).

```
python multi_feature_segment.py (--texture-cache TEXTURE_CACHE_FILE) image out_high out_low
```

depending on whether you use the texture-cache (if you run the original pipeline, this texture cache should be available)

if you have the texture-cache

```
python multi_feature_segment.py  --texture-cache /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/texture/100_0007_0001.npy /mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0001.JPG /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/high/100_0007_0001_trial.json /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/low/100_0007_0001_trial.json
```

if you do NOT have the texture-cache
```
python multi_feature_segment.py  /mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0003.JPG /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/high/100_0007_0003_trial.json /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/low/100_0007_0001_trial.json
```

### otsu_binarization.py

A script to be run on one image at a time to conduct otsu binary thresholding. To run this at scale, please check out [run_all_multifeature_thred.py](#runallmultifeaturethredpy).


```
python otsu_binarization.py image out
```

example:
```
python scripts/otsu_binarization.py /mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0005.JPG /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segment_trash/100_0007_0005_trial.json
```
### run_all_multifeature_thred.py 

A script to be run on a directory of images at a time to scale run one of the processes of your choice. The four choices include:
- otsu binarization, one-time run seen [here](#otsubinarizationpy)
- existing segmentation method, one-time run seen [here](#segmentpy)
- multi-feature voting segmentation method, one-time run seen [here](#multifeaturesegmentpy)
- watershed based on outputs of either existing or multi-feature thresholding methods, one-time run seen [here](#watershedsingleimagepy)

You will need to run the script by inputting the type of process you would like to run at scale:

```
python run_all_multifeature_thred.py [process_name] 
```

In our case, [process_name] can be replaced with `watershed`, `otsu`, `existing`, or `multifeature`.

And the follow instructions to input specific paths you might need, examples are shown below:

![existing segmentation method](https://github.com/tommyfuu/flower_map_new/blob/master/scripts/exp_pics/existing.png)

The multi-feature thresholding method is extremely similar to the existing one in terms of commands to run it, thus no example shown.

![otsu](https://github.com/tommyfuu/flower_map_new/blob/master/scripts/exp_pics/otsu.png)

![watershed](https://github.com/tommyfuu/flower_map_new/blob/master/scripts/exp_pics/watershed.png)


### segment.py

A script to be run on one image at a time to conduct thresholding using the existing strategy. To run this at scale, please check out [run_all_multifeature_thred.py](#runallmultifeaturethredpy).


```
python segment.py (--texture-cache TEXTURE_CACHE_FILE) image  out_high out_low
```

depending on whether you use the texture-cache (if you run the original pipeline, this texture cache should be available)

if you have the texture-cache 

```
python segment.py  --texture-cache /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/texture/100_0007_0002.npy /mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0002.JPG /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/high/100_0007_0002_trial.json /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/low/100_0007_0002_trial.json
```

if you do NOT have the texture-cache
```
python segment.py  /mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0002.JPG /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/high/100_0007_0002_trial.json /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/low/100_0007_0002_trial.json```
```

### visualizePolygons.py

A script to be run an image directory along with its json annotation to visualize all the annotations in image form.

```
python visualizePolygons.py dataDir img_postfix annFile endDir jsonDir option
```
example:
```
python visualizePolygons.py /mnt/biology/donaldson/tom/flower_map_new/newData/070921_North .JPG /mnt/biology/donaldson/tom/flower_map_new/annotations/070921_north.json /mnt/biology/donaldson/tom/flower_map_new/annotations_wspecies/20210709north_annotated /mnt/biology/donaldson/tom/flower_map_new/annotations_wspecies/jsons_20210709_north both
```

### watershed_single_image.py

A script to be run on one image at a time to conduct watershed based on thresholding from two confidence levels.


```
python watershed_single_image.py image seg_high seg_low out_json
```

Example:


```
python watershed_single_image.py /mnt/biology/donaldson/tom/flower_map_new/newData/070921_North/100_0007_0002.JPG /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/high/100_0007_0002.json /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/low/100_0007_0002.json /mnt/biology/donaldson/tom/flower_map_new/out/070921_North/segments/existing_watershed/100_0007_0002.json

```


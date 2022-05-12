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
ssss
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
python (--texture-cache TEXTURE_CACHE_DIRECTORY) cvat_path out
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



### multi_feature_segment.py

### otsu_binarization.py

### run_all_multifeature_thred.py

### segment.py

### visualizePolygons.py

### watershed_single_image.py



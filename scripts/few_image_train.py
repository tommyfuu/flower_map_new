#!/usr/bin/env python3
import argparse
from pathlib import Path

import numpy as np
import statsmodels.api as sm
from scipy import stats
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(
    description="Train generalized linear model to get coefficient for each variable."
)
parser.add_argument(
    "cvat_path", type=Path, help="the path to the folder from cvat containing annotations and images."
)
parser.add_argument(
    "out", help="the path to the file containing the json files generated to match the formats of preds and ground truth, as well as the output stats file"
)
parser.add_argument(
    "--texture-cache", type=Path, help=
    """
        The path to an npy file containing the texture of the image if already calculated.
        (Providing this option can speed up repeated executions of this script on the same input.)
        If this file does not exist, it will be created when the texture is calculated.
    """
)
args = parser.parse_args()

from pycocotools.coco import COCO
import os, sys, zipfile
import urllib.request
import shutil
import pandas as pd
import skimage.io as io
import matplotlib.pyplot as plt
import pylab
import json
import cv2 as cv
print("AAAAA", args.texture_cache)

# CONSTANTS
PARAMS = {
    'texture': {
        'window_radius': 2,
        'num_features': 6,
        'inverse_resolution': 50 # arya's value: 30
    },
    'blur': {
        'green_kernel_size': 5,
        'green_strength': 60,
        'contrast_kernel_size': 24 # potentially deletable
    },    
    'threshold': {
        'block_size': 2001,
        'C': 10,
    },
    # Tom's addition:
    'num_of_features': {
        'high': 4,
        'low': 2
    },
    # 'num_of_color_features': {
    #     'high': 3,
    #     'low': 2
    # },
    # 'num_of_texture_features': {
    #     'high': 2,
    #     'low': 1
    # },
    # TODO: will be useful in closing holes
    'morho': {
        'big_kernel_size': 24,
        'small_kernel_size': 5,
        'high': {
            'closing': 7,
            'opening': 4+15
        },
        'low': {
            'closing': 7,
            'opening': 4+7,
            'closing2': 14
        },
        'noise_removal': {
        'strength': 17,
        'templateWindowSize': 7,
        'searchWindowSize': 21
    },
    }
}

#json the address of the file needs to be set manually 
json_file=str(args.cvat_path)+'/annotations/instances_default.json'
# person_keypoints_val2017.json  # Object Keypoint  annotation format for types 
# captions_val2017.json  # Image Caption annotation format of 
data=json.load(open(json_file,'r'))
 
num_of_images = len(data['images'])
# i'm going to set the number of images that need to be extracted 82000 zhang 
for i in range(num_of_images):
    data_2 = {}
    data_2['info'] = data['info']
    data_2['licenses'] = data['licenses']
    data_2['images'] = [data['images'][i]]  #  extract only the first image 
    data_2['categories'] = data['categories']
    annotation = []

    #  find all its objects by imgid 
    imgID = data_2['images'][0]['id']
    for ann in data['annotations']:
        if ann['image_id'] == imgID:
            annotation.append(ann)

    data_2['annotations'] = annotation
    #  save to the new json file ， easy to view data features 
    #img_file  get image name 
    img_file=data_2['images'][0]['file_name']
    img_first=img_file.split(".")[0]

    # set store directory my store is in the current directory coco_single_object you need to manually create an empty folder under the folder 
    json.dump(data_2, open(str(args.cvat_path)+'/annotations/'+img_first+'.json', 'w'), indent=4)  # indent=4  more beautiful display 



import os
def sliding_window(img, fnctn, size, num_features=1, skip=0):
    """
        run fnctn over each sliding, square window of width 2*size+1, skipping every skip pixel
        store the result in a np arr of equal size as the img but with depth equal to num_features
    """
    # make a shape x num_features array, since there are num_features features
    new = np.empty(img.shape+(num_features,))
    # run a sliding window over the i and j indices
    for i in range(0, img.shape[0], skip):
        # we adjust for windows that would otherwise go over the edge of the frame
        i1 = max(0, i-size)
        i2 = min(i+size+1, img.shape[0])
        next_i = min(i+skip, img.shape[0])
        for j in range(0, img.shape[1], skip):
            j1 = max(0, j-size)
            j2 = min(j+size+1, img.shape[1])
            next_j = min(j+skip, img.shape[1])
            # call the function
            new[i:next_i,j:next_j,:] = fnctn(img[i1:i2,j1:j2])
    return new



def get_single_binaryImg(json_path,img_path,binary_img_save):
    endog_df = None
    exog_df = None
    dir=os.listdir(json_path)
    binary_img_l = []
    features_l = []
    for jfile in dir:
        if 'instances_default' not in jfile:
            annFile =os.path.join(json_path,jfile)
            coco = COCO(annFile)
            imgIds = coco.getImgIds()
            img = coco.loadImgs(imgIds[0])[0]

            # load and display instance annotations
            #  load the instance mask 
            catIds = []
            for ann in coco.dataset['annotations']:
                if ann['image_id'] == imgIds[0]:
                    catIds.append(ann['category_id'])

            annIds = coco.getAnnIds(imgIds=img['id'], catIds=catIds, iscrowd=None)
            width = img['width']
            height = img['height']
            anns = coco.loadAnns(annIds)
            mask_pic = np.zeros((height, width))
            for single in anns:
                mask_single = coco.annToMask(single)
                mask_pic += mask_single

            for row in range(height):
                for col in range(width):
                    if (mask_pic[row][col] > 0):
                        mask_pic[row][col] = 255
            print(np.unique(mask_pic))
            imgs = np.zeros(shape=(height, width, 3), dtype=np.float32)
            imgs = mask_pic

            binary_endog = imgs.flatten()
            print(binary_endog.shape, binary_endog)
            if endog_df is None:
                endog_df = pd.DataFrame(binary_endog, columns = ['binary_endog'])
            else:
                endog_df = endog_df.append(pd.DataFrame(binary_endog, columns = ['binary_endog']))

            print(endog_df.head())

            binary_img_l.append(imgs)
            name_img = img['file_name'].split(".")[0]
            print(name_img)
            # calculate all the features

            img = cv.imread(str(args.cvat_path)+'/images/'+name_img+'.JPG')

            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            print("TEXTURE_CACHE", args.texture_cache)
            if args.texture_cache is not None:
                texture_cache = str(args.texture_cache) + '/' + name_img + '.npy'
                if Path(texture_cache).exists():
                    texture = np.load(texture_cache)
                else:
                    print('calculating texture (this may take a while)')
                    texture = sliding_window(gray, features.glcm, *tuple([PARAMS['texture'][i] for i in ['window_radius', 'num_features', 'inverse_resolution']]))
                    str(args.texture_cache).mkdir(parents=True, exist_ok=True)
                    np.save(texture_cache, texture)
            # plt.imsave(binary_img_save + "/binary_" + img_name + ".png", imgs)
        
            # blur image to remove noise from grass
            print('blurring image to remove noise in the green and contrast values')
            blur_colors = cv.GaussianBlur(img, (PARAMS['blur']['green_kernel_size'],)*2, PARAMS['blur']['green_strength'])

            # 1. get all feature values
            ## colors; note that opencv uses bgr color format
            blur_blue = blur_colors[:,:,0]
            blur_green = blur_colors[:,:,1]
            blur_red = blur_colors[:,:,2]

            ## textural features
            blur_gradient = cv.Laplacian(gray, cv.CV_8UC1)
            blur_contrast = np.uint8(texture[:,:,0]*255/texture[:,:,0].max())
            blur_correlation = np.uint8(texture[:,:,4]*255)
            blur_energy = np.uint8(texture[:,:,3]*255/texture[:,:,3].max())
            blur_homogeneity = np.uint8(texture[:,:,2]*255)

            # 2. adaptive guassian thresholding
            ### TODO: as of 3/1 night the only feature that doesn't work at all is correlation.
            th_blue = blur_blue
            th_green = blur_green
            th_red = blur_red
            th_gradient = blur_gradient
            th_contrast = blur_contrast
            th_homogeneity = blur_homogeneity

            th_blue_1 = (th_blue/255).flatten()
            th_green_1 = (th_green/255).flatten()
            th_red_1 = (th_red/255).flatten()
            th_gradient_1 = (th_gradient/255).flatten()
            th_contrast_1 = (th_contrast/255).flatten()
            th_homogeneity_1 = (th_homogeneity/255).flatten()


            th_blue_1 = np.around(th_blue_1, decimals=3)
            th_green_1 = np.around(th_green_1, decimals=3)
            th_red_1 = np.around(th_red_1, decimals=3)
            th_gradient_1 = np.around(th_gradient_1, decimals=3)
            th_contrast_1 = np.around(th_contrast_1, decimals=3)
            th_homogeneity_1 = np.around(th_homogeneity_1, decimals=3)
            # th_correlation_1 = th_correlation/255
            # th_energy_1 = th_energy/255
            
            features_np = np.stack((th_blue_1, th_green_1, th_red_1, th_gradient_1, th_contrast_1, th_homogeneity_1)).T
            
            if exog_df is None:
                exog_df = pd.DataFrame(features_np, columns = ['th_blue', 'th_green', 'th_red', 'th_gradient', 'th_contrast', 'th_homogeneity'])
            else:
                exog_df = exog_df.append(pd.DataFrame(features_np, columns = ['th_blue', 'th_green', 'th_red', 'th_gradient', 'th_contrast', 'th_homogeneity']))

            print(exog_df.head())
            # # store all feature values
            # features_l.append([th_blue_1, th_green_1, th_red_1, th_gradient_1, th_contrast_1, th_homogeneity_1])
    return endog_df, exog_df
    # return binary_img_l, features_l
json_path = str(args.cvat_path)+'/annotations'
img_path = str(args.cvat_path)+'/images'
binary_img_save = str(args.cvat_path)+'/binary_images'
Path(binary_img_save).mkdir(parents=True, exist_ok=True)
endog_df, exog_df = get_single_binaryImg(json_path, img_path, binary_img_save)

endog_df = endog_df.sample(frac=0.0001, replace=False, random_state=1)
exog_df = endog_df[endog_df.index]
# train glm

glm_binom = sm.GLM(endog_df, exog_df, family=sm.families.Binomial()) # use the default gauassian family
res = glm_binom.fit()
print(res.summary())
print("PARAMS")
print(res.params)

with open(str(args.out)+'/glm_model_summary_1.txt', 'w') as f:
    f.write(str(res.summary()))

with open(str(args.out)+'/glm_model_params_1.txt', 'w') as f:
    f.write("PARAMS\n")
    f.write(str(res.params))
import cv2
import os
import random
import numpy as np
import time

import apriltag
options = apriltag.DetectorOptions(refine_edges=False)
detector = apriltag.Detector(options=options)

def l3_preprocess(image, **kwargs):
    # TODO: make stuff scale to image size
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=kwargs.get("clahe_clip_limit", 3), 
        tileGridSize=(kwargs.get("clahe_tile_size", 8), kwargs.get("clahe_tile_size", 8)))
    enhanced = clahe.apply(gray_image)

    edges = cv2.Canny(gray_image, 
        kwargs.get("canny_threshold_1", 50), kwargs.get("canny_threshold_1", 150))
    kernel = np.ones([kwargs.get("edge_refinement_kernel_size", 3), 
        kwargs.get("edge_refinement_kernel_size", 3)], np.uint8)
    dilated = cv2.dilate(edges, kernel, 1)

    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=1)

    thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 35,3)

    highlighted = cv2.bitwise_and(thresh, thresh, closed)
    return highlighted

def l2_preprocess(image, **kwargs):
    # TODO: make stuff scale to image size
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray_image, 
        kwargs.get("canny_threshold_1", 50), kwargs.get("canny_threshold_1", 150))
    kernel = np.ones([kwargs.get("edge_refinement_kernel_size", 3), 
        kwargs.get("edge_refinement_kernel_size", 3)], np.uint8)
    dilated = cv2.dilate(edges, kernel, 1)

    closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel, iterations=1)

    thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 
        kwargs.get("threshold_block_size", 35), kwargs.get("threshold_offset", 3))

    highlighted = cv2.bitwise_and(thresh, thresh, closed)
    return highlighted


def l1_preprocess(image, **kwargs):
    # TODO: make stuff scale to image size
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 
        kwargs.get("threshold_block_size", 35), kwargs.get("threshold_offset", 3))

    highlighted = cv2.bitwise_and(thresh, thresh, gray_image)

def detect(image):
    if len(image.shape) ==3:
        image =cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ids = detector.detect(image)
    if ids is None or len(ids)==0:
        return None
    return ids

raw = 0
proc = 0

tot_proc_time = 0
tot_raw_time = 0
    
for filename in os.listdir("Coprocessor/images")[1:-2]:
    print('\n'+filename, end='')
    image = cv2.imread("Coprocessor/images/" + filename)
    image = cv2.resize(image, [540, 960])
    image_array = l2_preprocess(image)
    start = time.time()
    proc_out = detect(image_array)
    proc_time = time.time()-start

    print(image.dtype)
    print(image_array.dtype)

    start = time.time()
    raw_out = detect(image)
    raw_time = time.time()-start
    if raw_out: 
        raw+=1
        print("raw")
    if proc_out: 
        proc +=1
        print("processed")
    tot_proc_time += proc_time
    tot_raw_time += raw_time
    cv2.imwrite("new_" + filename, image_array)

print("Raw: " + str(raw) + " Processed: " + str(proc) + " Raw Time: " + 
    str(tot_raw_time/len(os.listdir("Coprocessor/images")[1:-2])) + " Proc Time: " + 
    str(tot_proc_time/len(os.listdir("Coprocessor/images")[1:-2])))
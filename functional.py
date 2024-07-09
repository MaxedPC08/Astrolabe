import cv2
import numpy as np
from Locater import Locater
import os
import json


def find_camera_index():
    video_devices = []
    for device in os.listdir("/dev"):
        if device.startswith("video"):
            video_devices.append(f"/dev/{device}")

    for i in range(len(video_devices)):
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            print(f"Error: Could not open video device at index {i}")
            continue
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Could not read frame from video device at index {1}")
            continue
        print(f"Successfully opened video device at index {i}")
        cap.release()
        return i

locater = Locater()
cam = cv2.VideoCapture(find_camera_index())


def int_we(value, name):
    try:
        return int(value)
    except ValueError as e:
        raise ValueError(f'Error: Could not convert parameter -{name} with value "{value}" to an integer.') from e

def float_we(value, name):
    try:
        return float(value)
    except ValueError as e:
        raise ValueError(f'Error: Could not convert parameter -{name} with value "{value}" to a float.') from e

def json_we(value, name):
    try:
        return json.loads(value)
    except json.decoder.JSONDecodeError as e:
        raise ValueError(f'Error: Could not convert parameter -{name} with value "{value}" to a JSON object.') from e


async def processed_image(websocket):
    img = cv2.cvtColor(cam.read()[1], cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (160, 120))
    img, center, width = locater.locate(img)  # Locate the object in the image. Comment out this line if you don't want to process the image.
    # loc_from_center(center, width)
    image_array = np.asarray(img).flatten()  # You can adjust this if you want to get the center and width of the object
    await websocket.send(image_array.tobytes())


async def raw_image(websocket):
    img = cv2.cvtColor(cam.read()[1], cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (160, 120))
    image_array = np.asarray(img).flatten()
    await websocket.send(image_array.tobytes())

def switch_color(new_color=0):
    print(new_color)
    locater.active_color = min(int_we(new_color, "new_color"), len(locater.color_list) - 1)

def save_params(values):
    json_vals = json.loads(values)
    locater.color_list = json_vals[:-1]
    locater.active_color = json_vals[-1]
    cam.set(cv2.CAP_PROP_BRIGHTNESS, int(locater.color_list[locater.active_color]["brightness"]))
    cam.set(cv2.CAP_PROP_CONTRAST, int(locater.color_list[locater.active_color]["contrast"]))
    with open('params.json', 'w') as f:
        json.dump(locater.color_list, f, indent=4)

functionDict = {
    "processed_image": processed_image,
    "pi": processed_image,
    "raw_image": raw_image,
    "ri": raw_image,
    "switch_color": switch_color,
    "sc": switch_color,
    "save_params": save_params,
    "sp": save_params
}

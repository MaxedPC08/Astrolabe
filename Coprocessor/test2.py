import websockets
import asyncio
import base64
import json
import numpy as np
import cv2
import time

def print_dict(json_object):
    for key, value in json_object.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")

def list_dict(json_object):
    output = []
    for key, value in json_object.items():
        if isinstance(value, dict):
            output.append(f"{key}:")
            for sub_key, sub_value in value.items():
                output.append([f"  {sub_key}", sub_value])
        else:
            output.append([key, value])
    return output

async def websocket_client():
    uri = "ws://127.0.0.1:50000"  # replace with your websocket server url
    async with websockets.connect(uri) as websocket:
        message = input("Enter your message: ")
        await websocket.send(message)
        start_time = time.time()
        response = await websocket.recv()
        if "image_string" in response and not "fake_image_string" in response:
            response_json = json.loads(response)
            image_string = response_json["image_string"]
            encoded_img = cv2.imdecode(np.frombuffer(base64.b64decode(image_string), np.uint8), cv2.IMREAD_COLOR)
            cv2.imwrite("output.jpg", encoded_img)
            response_json["image_string"] = "Image String Hidden for Clarity. Check output.jpg"
            response = json.dumps(response_json)

        print_dict(json.loads(response))
        end_time = time.time()
        fps = 1 / (end_time - start_time)
        print(f"FPS: {fps:.2f}")


while True:
    asyncio.run(websocket_client())

"""
{"function":"apriltag","return_image":true}

{
  "function": "set_camera_params",
  "auto_exposure": 0, "fps": 60, "buffer_size": 1, "brightness": 0, "contrast": 0, "exposure": -3, "gain": 0, "autofocus": 0, "focus": 0, "downscale_factor": 4
}

"""
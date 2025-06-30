import websockets
import asyncio
import base64
import json
import numpy as np
import cv2
import time

def stringify_response(json_object):
    output = []
    for key in json_object.keys():
        output.append(stringify_response(json_object[key]))

def print_dict(json_object):
    for key, value in json_object.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")


async def websocket_client():
    uri = "ws://127.0.0.1:50001"  # replace with your websocket server url
    async with websockets.connect(uri) as websocket:
        start_time = time.time()
        message = '{"function":"apriltag","return_image":true}' # input("Enter your message: ")
        await websocket.send(message)
        response = await websocket.recv()
        if False: #"image_string" in response:
            response_json = json.loads(response)
            image_string = response_json["image_string"]
            encoded_img = cv2.imdecode(np.frombuffer(base64.b64decode(image_string), np.uint8), cv2.IMREAD_COLOR)
            cv2.imwrite("output.jpg", encoded_img)
            # response_json["image_string"] = "Image String Hidden for Clarity. Check output.jpg"
            response = json.dumps(response_json)

        # print(f"Received: {response}")
        end_time = time.time()
        fps = 1 / (end_time - start_time)
        print(f"FPS: {fps:.2f}")


while True:
    asyncio.run(websocket_client())

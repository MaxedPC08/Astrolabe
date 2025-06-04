import websockets
import asyncio
import base64
import json
import numpy as np
import cv2

async def websocket_client():
    uri = "ws://127.0.0.1:50000"  # replace with your websocket server url
    async with websockets.connect(uri) as websocket:
        message = input("Enter your message: ")
        await websocket.send(message)
        response = await websocket.recv()
        if "image_string" in response:
            response_json = json.loads(response)
            image_string = response_json["image_string"]
            encoded_img = cv2.imdecode(np.frombuffer(base64.b64decode(image_string), np.uint8), cv2.IMREAD_COLOR)
            cv2.imwrite("output.jpg", encoded_img)
            response_json["image_string"] = "Image String Hidden for Clarity. Check output.jpg"
            response = json.dumps(response_json)

        print(f"Received: {response}")


while True:
    asyncio.run(websocket_client())

import asyncio
import websockets
import socket
import cv2
import numpy as np
import time
from Locater import Locater, loc_from_center



#Set up an opencv camera object
cam=cv2.VideoCapture(0)

# Get the IP address of the Ethernet interface
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ethernet_ip = s.getsockname()[0]
s.close()


# WebSocket server
async def websocket_server(websocket, path):
    """
    This function is the main function for the WebSocket server. It receives images from the client and sends them back.
    :param websocket:
    :param path:
    :return:
    """
    async for message in websocket:
        if message == "processed":
            #Only send images if the client requests it. This is to prevent the server from sending images when the client is not ready.
            #Read the image from the camera
            start = time.time()
            img = cv2.cvtColor(cam.read()[1], cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (160, 120))
            img, center, width = locater.locate(img) #Locate the object in the image. Comment out this line if you don't want to process the image.
            #loc_from_center(center, width)
            image_array = np.asarray(img).flatten() #You can adjust this if you want to get the center and width of the object
            await websocket.send(image_array.tobytes()) # Center is y, x, from top left
        elif message == "raw":
            #Read the image from the camera
            start = time.time()
            img = cv2.cvtColor(cam.read()[1], cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (160, 120))
            image_array = np.asarray(img).flatten()
            await websocket.send(image_array.tobytes())
        elif message[:6] == "values":
            print(f"Received message: {message}")
            values = message[7:].split(",")
            locater.red_val = int(values[0])
            locater.green_val = int(values[1])
            locater.blue_val = int(values[2])
            locater.difference_val = int(values[3])
            locater.blur_val = int(values[4])

            # Save the new values to the params.txt file
            with open('params.txt', 'w') as f:
                f.write(f"red: {locater.red_val}\n")
                f.write(f"green: {locater.green_val}\n")
                f.write(f"blue: {locater.blue_val}\n")
                f.write(f"blur: {locater.blur_val}\n")
                f.write(f"difference: {locater.difference_val}\n")

            print(f"Set values to {values}")

if __name__ == "__main__":
    locater = Locater()
    start_server = websockets.serve(websocket_server, ethernet_ip, 8765, ping_timeout=None, ping_interval=None)

    print(f"WebSocket server listening on {ethernet_ip}:8765")

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
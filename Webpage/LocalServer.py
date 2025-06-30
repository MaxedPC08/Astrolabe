import websockets
import asyncio
import json
import time
import queue
import base64
import cv2
import numpy as np
import threading
from collections import deque

def list_dict(json_object, prefix='', allow_list=True):
    output = []
    for key, value in json_object.items():
        if key == "image_string":
            output.append([key, prefix + "Image displayed."])
        elif isinstance(value, dict):
            output.append(prefix + f"{key}:")
            for sub_key, sub_value in value.items():
                output.append([prefix + f"- {sub_key}", str(sub_value)])
        elif isinstance(value, list) and allow_list:
            output.append(f"{key}:")
            for i, val in enumerate(value):
                output.append(f"- Item {i+1}:")
                output.extend(list_dict(val, "--- ", False))
        else:
            output.append([prefix + str(key), str(value)])
    return output

class LocalServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.function_info = None
        self.active_connection = None
        self.current_camera_port = port
        self.fps_times = deque(maxlen=30)  # Store last 30 frame times for FPS calculation
        self.current_fps = 0
        
        # Queue for sharing images between websocket thread and Flask
        self.image_queue = queue.Queue(maxsize=1)
        self.last_response = {}

        # Queue for sending commands from Flask to websocket
        self.command_queue = queue.Queue()
        self.last_command = self.repeat_command = json.dumps({"function": "raw"})
        self.repeat = True
        
        # Start websocket client in a background thread
        self.is_running = True
        self.ws_thread = threading.Thread(target=self.run_websocket_client)
        self.ws_thread.daemon = True
        self.ws_thread.start()
    
    def switch_camera(self, port):
        """Switch to a different camera by port"""
        self.current_camera_port = port
        # Close the current connection to force a reconnect with new port
        if self.active_connection:
            asyncio.run(self.active_connection.close())
            self.active_connection = None

    # Websocket client that runs in a separate thread
    async def websocket_client(self):
        uri = f"ws://{self.ip}:{self.current_camera_port}"
        try:
            async with websockets.connect(uri) as websocket:
                self.active_connection = websocket
                while True:
                    start_time = time.time()
                    try:
                        if self.repeat:
                            command = self.repeat_command
                        else:
                            try:
                                command = self.command_queue.get(timeout=0.1)
                            except queue.Empty:
                                continue

                        self.last_command = command
                        
                        await websocket.send(command)
                        response = await websocket.recv()
                        try:
                            response_json = json.loads(response)
                            self.last_response = response_json  # Store the latest response
                            if "image_string" in response_json and not "fake_image_string" in response:
                                image_string = response_json["image_string"]
                                encoded_img = cv2.imdecode(np.frombuffer(base64.b64decode(image_string), np.uint8), cv2.IMREAD_COLOR)
                                if not self.image_queue.empty():
                                    try:
                                        self.image_queue.get_nowait()
                                    except queue.Empty:
                                        pass
                                self.image_queue.put(encoded_img)
                                self.last_response["image_string"] = "Image displayed."
                        except json.JSONDecodeError:
                            print("Received non-JSON response")
                        except Exception as e:
                            print(f"Error processing image: {e}")

                        self.current_fps = 1 / (time.time() - start_time)

                    except Exception as e:
                        print(f"Error sending command: {e}")

                    elapsed = time.time() - start_time
                    await asyncio.sleep(max(0.001, 0.05 - elapsed))
        except Exception as e:
            print(f"Websocket error: {e}")
            self.active_connection = None
            await asyncio.sleep(2)

    # Start the asyncio event loop in a separate thread
    def run_websocket_client(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while self.is_running:
            try:
                loop.run_until_complete(self.websocket_client())
            except Exception as e:
                print(f"Websocket client error: {e}")
            time.sleep(2)  # Wait before attempting to reconnect

    def generate_frames(self):
        frame = np.zeros((480, 640, 3), np.uint8)
        cv2.putText(frame, "Waiting for stream...", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        while True:
            try:
                if not self.image_queue.empty():
                    frame = self.image_queue.get()

                _, buffer = cv2.imencode('.jpg', frame)
                frame_data = buffer.tobytes()
                
                # Yield the frame as part of a multipart response
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
                      
                time.sleep(0.005)  # Small delay to control frame rate
            except Exception as e:
                print(f"Error in generate_frames: {e}")
                # In case of error, yield an error frame
                error_frame = np.zeros((480, 640, 3), np.uint8)
                cv2.putText(error_frame, "Stream Error", (220, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                _, buffer = cv2.imencode('.jpg', error_frame)
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    def send_command(self, command):
        """Add a command to the queue to be sent via websocket"""
        filtered_command = {}
        command_json = json.loads(command)
        for key, value in command_json.items():
            if value != "":
                filtered_command[key] = value

        command = json.dumps(filtered_command)
        print(f"Sending command: {command}")
        if not self.repeat:
            # Empty the queue before putting a new command
            while not self.command_queue.empty():
                try:
                    self.command_queue.get_nowait()
                except queue.Empty:
                    break
            self.command_queue.put(command)
        else:
            self.repeat_command = command
    
    def get_fps(self):
        """Return the current FPS"""
        return self.current_fps
    
    def get_return_data(self):
        """Return the last response as a list of [name, value] pairs."""
        return list_dict(self.last_response)
    
    def set_repeat(self, repeat):
        print(f"Setting repeat to: {repeat}")
        self.repeat = repeat
        
    
    def cleanup(self):
        """Clean up resources"""
        self.is_running = False
        if self.active_connection:
            asyncio.run(self.active_connection.close())
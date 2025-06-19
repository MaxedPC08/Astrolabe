from flask import Flask, Response, render_template_string, request
import cv2
import asyncio
import websockets
import base64
import json
import numpy as np
import threading
import time
import queue

app = Flask(__name__)

prev_frame = time.time()

# Queue for sharing images between websocket thread and Flask
image_queue = queue.Queue(maxsize=1)
# Queue for sending commands from Flask to websocket
command_queue = queue.Queue()

# HTML template with command input field
with open("flask.html", "r") as file:
    HTML_TEMPLATE = file.read()
# Websocket client that runs in a separate thread
async def websocket_client():
    uri = "ws://127.0.0.1:50000"  # replace with your websocket server url
    try:
        async with websockets.connect(uri) as websocket:
            command_task = asyncio.create_task(process_commands(websocket))
            
            while True:
                await websocket.send("{'function':'apriltag','return_image':true}")  # Default command to get an image
                response = await websocket.recv()
                
                try:
                    response_json = json.loads(response)
                    if "image_string" in response_json:
                        image_string = response_json["image_string"]
                        encoded_img = cv2.imdecode(np.frombuffer(base64.b64decode(image_string), np.uint8), cv2.IMREAD_COLOR)
                        
                        # Put the new image in the queue, replacing any old one
                        if not image_queue.empty():
                            try:
                                image_queue.get_nowait()  # Remove old image
                            except queue.Empty:
                                pass
                        image_queue.put(encoded_img)
                except json.JSONDecodeError:
                    print("Received non-JSON response")
                except Exception as e:
                    print(f"Error processing image: {e}")
                
                await asyncio.sleep(0.001)  # Small delay to not flood the server
    except Exception as e:
        print(f"Websocket error: {e}")
        # Wait before attempting to reconnect
        await asyncio.sleep(5)

# Process commands from the web interface
async def process_commands(websocket):
    while True:
        try:
            if not command_queue.empty():
                command = command_queue.get()
                await websocket.send(command)
                response = await websocket.recv()
                print(f"Command response: {response}")
        except Exception as e:
            print(f"Error sending command: {e}")
        await asyncio.sleep(0.001)  # Check for new commands periodically

# Start the asyncio event loop in a separate thread
def run_websocket_client():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            loop.run_until_complete(websocket_client())
        except Exception as e:
            print(f"Websocket client error: {e}")
        time.sleep(5)  # Wait before attempting to reconnect

def generate_frames():
    frame = np.zeros((480, 640, 3), np.uint8)
    # cv2.putText(default_frame, "Waiting for stream...", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    while True:
        try:
            if not image_queue.empty():
                frame = image_queue.get()
                
            # Encode the frame in JPEG format
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

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.get_json()
    command = data.get('command', '')
    if command:
        command_queue.put(command)
    return {'status': 'ok'}

if __name__ == '__main__':
    # Start the websocket client in a separate thread
    threading.Thread(target=run_websocket_client, daemon=True).start()
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=5000, debug=False)
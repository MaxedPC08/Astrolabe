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
import GlobalServer

app = Flask(__name__)

# HTML template with command input field
with open("flask.html", "r") as file:
    HTML_TEMPLATE = file.read()

global_server = GlobalServer()

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
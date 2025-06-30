from flask import Flask, Response, render_template, request, jsonify
import asyncio
from Webpage.GlobalServer import GlobalServer
from Webpage.LocalServer import LocalServer
import os, json

app = Flask(__name__, template_folder='.')

# Dictionary to store local servers for each camera (key = ip:port)
camera_servers = {}
active_camera = {"ip": "127.0.0.1", "port": 50001}  # Default camera
default_ip = "127.0.0.1"
default_port = 50001  # Default camera port (Camera #1)
PARAMS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_command_params.json")

@app.route('/')
def index():
    return render_template('flask.html')

@app.route('/video_feed')
def video_feed():
    # Get the active camera
    ip = active_camera["ip"]
    port = active_camera["port"]
    server_key = f"{ip}:{port}"
    
    # If no active camera, use default
    if server_key not in camera_servers:
        # Create server for the camera if it doesn't exist
        server = LocalServer(ip, port)
        camera_servers[server_key] = server
    else:
        server = camera_servers[server_key]
    
    return Response(server.generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/connect_camera', methods=['POST'])
def connect_camera():
    global active_camera
    data = request.get_json()
    ip = data.get('ip', default_ip)
    port = int(data.get('port', default_port))
    
    # Update active camera
    active_camera = {"ip": ip, "port": port}
    server_key = f"{ip}:{port}"
    
    try:
        # If server doesn't exist for this IP:port, create it
        if server_key not in camera_servers:
            server = LocalServer(ip, port)
            camera_servers[server_key] = server
        
        return jsonify({"status": "success", "message": f"Connected to camera at {ip}:{port}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.get_json()
    command = data.get('command')
    ip = data.get('ip', active_camera["ip"])
    port = int(data.get('port', active_camera["port"]))
    server_key = f"{ip}:{port}"
    
    if server_key in camera_servers:
        server = camera_servers[server_key]
        server.send_command(command)
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Server not found for selected camera"})

@app.route('/get_fps')
def get_fps():
    ip = active_camera["ip"]
    port = active_camera["port"]
    server_key = f"{ip}:{port}"
    
    if server_key in camera_servers:
        server = camera_servers[server_key]
        return jsonify({"fps": server.get_fps()})
    return jsonify({"fps": 0})

@app.route('/get_function_info', methods=['POST'])
def get_function_info():
    print("Fetching function info from GlobalServer")
    data = request.get_json()
    ip = data.get('ip', default_ip)
    port = int(data.get('port', 50000))  # GlobalServer is always at 50000
    gs = GlobalServer(ip, 50000)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        info = loop.run_until_complete(gs.get_function_info())
        return jsonify({"status": "success", "info": info})
    except Exception as e:
        print(f"Error fetching function info: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/set_repeat', methods=['POST'])
def set_repeat():
    data = request.get_json()
    repeat = bool(data.get('repeat', False))
    1
    ip = data.get('ip', active_camera["ip"])
    port = int(data.get('port', active_camera["port"]))
    server_key = f"{ip}:{port}"
    
    if server_key in camera_servers:
        server = camera_servers[server_key]
        server.set_repeat(repeat)
        print(f"Repeat set to: {repeat}")
        return jsonify({"status": "success", "repeat": repeat})
    return jsonify({"status": "error", "message": "Server not found for selected camera"})

@app.route('/get_return_data')
def get_return_data():
    ip = active_camera["ip"]
    port = active_camera["port"]
    server_key = f"{ip}:{port}"

    if server_key in camera_servers:
        server = camera_servers[server_key]
        return jsonify(server.get_return_data())
    return jsonify({"status": "error", "message": "Server not found for selected camera"})



def load_command_params():
    if os.path.exists(PARAMS_FILE):
        with open(PARAMS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_command_params(params):
    with open(PARAMS_FILE, "w") as f:
        json.dump(params, f, indent=2)

@app.route('/get_saved_params', methods=['GET'])
def get_saved_params():
    return jsonify(load_command_params())

@app.route('/save_params', methods=['POST'])
def save_params():
    params = request.get_json()
    save_command_params(params)
    return jsonify({"status": "success"})

def run_app(port=5000):
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    run_app()

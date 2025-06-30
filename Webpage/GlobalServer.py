import websockets
import asyncio
import json

class GlobalServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.function_info = None
        self.camera_info = None

    async def get_function_info(self):
        if self.function_info is not None:
            print("Using cached function info")
            return self.function_info
        
        uri = f"ws://{self.ip}:{self.port}"
        async with websockets.connect(uri) as websocket:
            # Send your request here
            await websocket.send(json.dumps({"function": "function_info"}))
            
            # Receive response
            response = await websocket.recv()
            
            # Parse JSON response into dictionary
            self.function_info = json.loads(response)
            return self.function_info
    
    async def get_cameras(self):
        uri = f"ws://{self.ip}:{self.port}"
        async with websockets.connect(uri) as websocket:
            # Send your request here
            await websocket.send(json.dumps({"function": "camera_info"}))
            
            # Receive response
            response = await websocket.recv()
            
            # Parse JSON response into dictionary
            self.camera_info = json.loads(response)
            return self.camera_info
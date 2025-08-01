import json
import psutil
import platform
import os


def get_raspberry_pi_performance():
    """
    This function gets the performance information of the Raspberry Pi such as temperature, CPU usage, memory usage,
    disk usage, and system information.
    :return: a dictionary containing the performance information
    """

    # Get temperature
    temp_output = os.popen("vcgencmd measure_temp").readline()
    temp_value = temp_output.replace("temp=", "").replace("'C\n", "")

    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # Get memory usage
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent

    # Get disk usage
    disk_info = psutil.disk_usage('/')
    disk_usage = disk_info.percent

    # Get system information
    system_info = platform.uname()

    # Combine all information into a dictionary
    performance_info = {
        "temperature": temp_value,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "disk_usage": disk_usage,
        "system": system_info.system,
        "node_name": system_info.node,
        "release": system_info.release,
        "version": system_info.version,
        "machine": system_info.machine,
        "processor": system_info.processor
        
    }

    return performance_info


class GlobalFunctionalObject:
    def __init__(self, name=None, serial_number=None, host_data=None):
        self.host_data = host_data
        self.function_dict = {
                "hardware_info": self.hardware_info,
                "function_info": self.function_info,
                "camera_info": self.camera_info
            }
        
    async def camera_info(self, websocket, *args, **kwargs):
        await websocket.send(json.dumps(self.host_data))

    async def hardware_info(self, websocket, *args, **kwargs):
        hardware = get_raspberry_pi_performance()
        await websocket.send(json.dumps(hardware))

    async def function_info(self, websocket, *args, **kwargs):
        hardware_info = {"description":"The command will return a lot of information about the current hardware.",
                     "arguments": {},
                     "returns":
                        {"temperature":{"type":"float",
                                     "description":"Temperature of CPU",
                                     "guarantee":True},

                        "cpu_usage":{"type":"float",
                                     "description":"The amount of the CPU being used.",
                                     "guarantee":True},

                        "memory_usage":{"type":"float",
                                     "description":"The amount of memory being used.",
                                     "guarantee":True},
                        
                        "disk_usage":{"type":"float",
                                     "description":"The disk usage.",
                                     "guarantee":True},
                        
                        "system":{"type":"string",
                                     "description":"What OS the system is running.",
                                     "guarantee":False},
                        
                        "node_name":{"type":"string",
                                     "description":"Name of the node.",
                                     "guarantee":False},

                        "release":{"type":"string",
                                     "description":"What release the OS is on at this point.",
                                     "guarantee":False},
                        
                        "version":{"type":"string",
                                     "description":"What version of the os currently running.",
                                     "guarantee":False},
                                     
                        "machine":{"type":"string",
                                     "description":"The architecture of the CPU.",
                                     "guarantee":False},

                        "processor":{"type":"float",
                                     "description":"More detailed information about the CPU.",
                                     "guarantee":True}
                     }}
        
        connection_info = {"description":"The command will return a lot of information about the current camera setup.",
                     "arguments": {},
                     "returns":
                        {"connections":{"type":"dictionary",
                                     "description":"Information about the connections to the cameras and other open websockets.",
                                     "guarantee":True}
                     }}
        
        functions = {
            "hardware_info": hardware_info,
            "camera_info": connection_info
        }
        await websocket.send(json.dumps(functions))

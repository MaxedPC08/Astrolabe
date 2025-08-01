import time
from Server import Server
import os
import psutil
import multiprocessing
import subprocess
import sys
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Coprocessor.CameraFunctional import CameraFunctionalObject
from Coprocessor.GlobalFunctional import GlobalFunctionalObject
from Coprocessor.Reinforcement.ControllerFunctional import ControllerFunctionalObject
from Coprocessor.Webpage.app import run_app
from Coprocessor.usb import copy_to_usb

MOUNT_DIR = "/mnt/usb_temp_mount"

def name_valid_cams():
    try:
        device_list = [f"/dev/{device}" for device in os.listdir("/dev") if device.startswith("video")]
    except:
        return []

    if len(device_list) == 0:
        return []

    known_devices = []

    for device in device_list:
        p = subprocess.Popen(
            f"udevadm info --name={device} | awk '/ID_SERIAL=/' | cut -d '=' -f 2 | tr '\n' '-' | sed 's/.$//'",
            stdout=subprocess.PIPE, shell=True)
        (output, _) = p.communicate()
        if output.decode('utf-8'):
            p = subprocess.Popen(
                f"udevadm info --name={device} | awk '/ID_PATH_TAG=/' | cut -d '=' -f 2 | tr '\n' '-'",
                stdout=subprocess.PIPE, shell=True)
            (path, _) = p.communicate()
            p = subprocess.Popen(
                f"udevadm info --name={device} | awk '/ID_SERIAL|ID_USB_VENDOR_ID|ID_USB_MODEL_ID/' | cut -d '=' -f 2 | tr '\n' '-' | sed 's/.$//'",
                stdout=subprocess.PIPE, shell=True)
            (id, _) = p.communicate()
            p = subprocess.Popen(
                f"udevadm info --name={device} | awk '/DEVLINKS=/' | cut -d '=' -f 2 | tr ' ' '\n' | awk '/by-path/'", #  | tr ' //' '/n' | awk '/by-path/'
                stdout=subprocess.PIPE, shell=True)
            (device_path, _) = p.communicate()
            known_devices.append([path.decode('utf-8')[:-1], device_path.decode('utf-8')[:-1], id.decode('utf-8')[:-1]])

    known_devices = sorted(known_devices, key=lambda x: x[1], reverse=True)
    known_devices = list({path: [device, id, path] for path, device, id in known_devices}.values())
    serial_numbers = [device[1] for device in known_devices]
    sn_counts = {sn: serial_numbers.count(sn) for sn in set(serial_numbers)}
    known_devices = [[device[0], device[1]+"-"+device[2] if sn_counts[device[1]]>1 else device[1]] for device in known_devices]
    known_devices = sorted(known_devices, key=lambda x: x[1])
    known_devices = [[device[0].split("\n")[0], device[1]] for i, device in enumerate(known_devices)]
    return known_devices

def start_server_with_affinity(server, cpu_core):
    p = multiprocessing.Process(target=server.start_server)
    p.start()
    psutil.Process(p.pid).cpu_affinity([cpu_core])
    return p


if __name__ == "__main__":
    try:
        cams_list = name_valid_cams()
        while cams_list == []:
            cams_list = name_valid_cams()
            time.sleep(5)
        
        print(f"Found {len(cams_list)} camera(s)")\
        
        servers = []
        processes = []

        host_data = {}

        
        for i, (camera_index, sn) in enumerate(cams_list):
            host_data[sn] = {"port": 50001 + i, "cam_index": camera_index}
            server = Server(50001 + i, CameraFunctionalObject, camera_index, sn)
            servers.append(server)
            processes.append(start_server_with_affinity(server, i % os.cpu_count()))

        host_data["Controllers"] = {"port": 49999, "host_name": "Controllers"}
        server = Server(49999, ControllerFunctionalObject, 0, "Global",  host_data=host_data)

        host_data["Global"] = {"port": 50000, "host_name": "Global", "cam_index": -2}
        server = Server(50000, GlobalFunctionalObject, -2, "Global",  host_data=host_data)
        servers.append(server)
        processes.append(start_server_with_affinity(server, 0))

        usb_storage_devices = []
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, ".saves")
        usb_found = copy_to_usb(data_path, "Astrolabe")
        
        if usb_found:
            run_app()

        for p in processes:
            p.join()
    finally:
        # Clean up processes if they are still running
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join()

        # Optionally, clean up any temporary files or directories here
        coprocessor_output_dir = os.path.join(os.path.dirname(__file__), "output")
        if os.path.exists(coprocessor_output_dir):
            shutil.rmtree(coprocessor_output_dir)

        print("Coprocessor server(s) stopped and cleaned up.")


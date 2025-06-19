from Server import Server
import os
import psutil
import multiprocessing
import subprocess
from constants import TEST_MODE_FALLBACK, TEST_MODE_FALLBACK

def name_valid_cams():
    try:
        device_list = [f"/dev/{device}" for device in os.listdir("/dev") if device.startswith("video")]
    except:
        if TEST_MODE_FALLBACK:
            return [[-1, "no-cameras-found"]]

    if len(device_list) == 0:
        return

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
    cams_list = name_valid_cams()
    print(f"Found {len(cams_list)} camera(s)")\
    
    servers = []
    processes = []

    host_data = []

    if cams_list[0][0] == -1 and TEST_MODE_FALLBACK:
        host_data.append({"port": 50001, "host_name": "Local-Image-Test-Mode", "cam_index": -1})
        server = Server(-1, "Local-Image-Test-Mode", 50001)
        servers.append(server)
        processes.append(start_server_with_affinity(server, 0))
    else:
        for i, (camera_index, sn) in enumerate(cams_list):
            host_data.append({"port": 50001 + i, "host_name": sn, "cam_index": camera_index})
            server = Server(camera_index, sn, 50001 + i)
            servers.append(server)
            processes.append(start_server_with_affinity(server, i % os.cpu_count()))


    host_data.append({"port": 5000, "host_name": "Global", "cam_index": -2})
    server = Server(-2, "Global", 50000)
    servers.append(server)
    processes.append(start_server_with_affinity(server, 0))

    for p in processes:
        p.join()


from Server import Server
import os
import psutil
import multiprocessing
import subprocess

def name_valid_cams():
    device_list = [f"/dev/{device}" for device in os.listdir("/dev") if device.startswith("video")]
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
    return known_devices

def start_server_with_affinity(server, cpu_core):
    p = multiprocessing.Process(target=server.start_server)
    p.start()
    psutil.Process(p.pid).cpu_affinity([cpu_core])
    return p


if __name__ == "__main__":
    cams_list = name_valid_cams()
    print(f"Found {len(cams_list)} camera(s)")

    servers = []
    processes = []
    for i, (camera_index, sn) in enumerate(cams_list):
        server = Server(camera_index, sn, 50000 + i)
        servers.append(server)
        processes.append(start_server_with_affinity(server, i % os.cpu_count()))

    for p in processes:
        p.join()


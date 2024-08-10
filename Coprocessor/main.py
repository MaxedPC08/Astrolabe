from Server import Server
import cv2
import os
import psutil
import multiprocessing
import subprocess
import time


def delete_and_reload_camera(device, driver='uvcvideo'):
    # Release the camera if it is currently in use
    cap = cv2.VideoCapture(device)
    if cap.isOpened():
        cap.release()

    # Delete the camera device file
    delete_command = f"sudo rm {device}"
    try:
        subprocess.run(delete_command, shell=True, check=True)
        print(f"Camera device {device} has been deleted.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to delete camera device {device}: {e}")

    # Reload the camera driver
    reload_command = f"sudo modprobe -r {driver} && sudo modprobe {driver}"
    try:
        subprocess.run(reload_command, shell=True, check=True)
        print(f"Camera driver {driver} has been reloaded.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to reload camera driver {driver}: {e}")


def find_camera_index():
    video_devices = [f"/dev/{device}" for device in os.listdir("/dev") if device.startswith("video")]
    cam_list = []
    for i, device in enumerate(video_devices):
        start = time.time()
        temp_cam = cv2.VideoCapture(device)
        temp_cam.release()

        cap = cv2.VideoCapture(device)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret, _ = cap.read()

        if not ret and not cap.isOpened() and time.time() - start > 0.1:
            delete_and_reload_camera(device)
            cap = cv2.VideoCapture(device)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            ret, _ = cap.read()

        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                cam_list.append(device)
            cap.release()
    return cam_list


def start_server_with_affinity(server, cpu_core):
    p = multiprocessing.Process(target=server.start_server)
    p.start()
    psutil.Process(p.pid).cpu_affinity([cpu_core])
    return p


if __name__ == "__main__":
    camera_indexes = find_camera_index()
    print(f"Found {len(camera_indexes)} camera(s)")
    servers = []
    processes = []
    for i, camera_index in enumerate(camera_indexes):
        server = Server(camera_index, 50000 + i)
        servers.append(server)
        processes.append(start_server_with_affinity(server, i % os.cpu_count()))

    for p in processes:
        p.join()

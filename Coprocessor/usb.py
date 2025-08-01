#!/usr/bin/env python3

import os
import shutil
import subprocess

MOUNT_DIR = "/mnt/usb_temp_mount"

def copy_to_usb(source_dir, target_subdir="Astrolabe"):
    """
    Detects a removable USB drive, mounts it, copies all files from `source_dir`
    to a subdirectory (`target_subdir`) on the USB, then unmounts the device.
    """

    # Step 1: Find unmounted USB partitions
    def get_removable_partitions():
        result = subprocess.run(
            ["lsblk", "-rno", "NAME,RM,TYPE,MOUNTPOINT"],
            stdout=subprocess.PIPE, text=True
        )

        removable_partitions = []
        for line in result.stdout.strip().split("\n"):
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            name, rm, dev_type = parts[:3]
            mountpoint = parts[3] if len(parts) > 3 else ""

            if rm == "1" and dev_type == "part" and mountpoint == "":
                removable_partitions.append(f"/dev/{name}")
        return removable_partitions

    # Step 2: Mount device
    def mount_device(dev_path, mount_point):
        if os.geteuid() == 0:
            os.makedirs(mount_point, exist_ok=True)
            subprocess.run(["mount", dev_path, mount_point], check=True)
            return True
        else:
            print("This script must be run as root to mount devices. Files not copied.")
            return False

    # Step 3: Copy files
    def copy_files(src, dst):
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)



    partitions = get_removable_partitions()
    if not partitions:
        return False

        # Begin main copy operation
    if not os.path.isdir(source_dir):
        return True

    dev_path = partitions[0]
    
    try:
        mounted = mount_device(dev_path, MOUNT_DIR)
    except subprocess.CalledProcessError as e:
        return True

    
    if mounted:
        try:
            usb_target_path = os.path.join(MOUNT_DIR, target_subdir)
            copy_files(source_dir, usb_target_path)

            if os.path.isdir(source_dir):
                for filename in os.listdir(source_dir):
                    file_path = os.path.join(source_dir, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception:
                        pass
        finally:
            subprocess.run(["umount", MOUNT_DIR])
            if os.path.exists(MOUNT_DIR):
                shutil.rmtree(MOUNT_DIR)
            
            
    return True

# Example usage:
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "cache")
    copy_to_usb(data_path, "Astrolabe")

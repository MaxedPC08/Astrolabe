#!/usr/bin/env python3
import cv2
import numpy as np
import time

def capture_stereo_vision_with_depth():
    """Capture stereo vision from two USB cameras, compute depth map, and print frame rate."""
    # Initialize two USB cameras (at indices 0 and 2 as specified)
    cap_left = cv2.VideoCapture(0)
    cap_right = cv2.VideoCapture(2)

    # Set resolution (640x480 as specified)
    cap_left.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap_left.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap_right.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap_right.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap_left.isOpened() or not cap_right.isOpened():
        print("Error: Could not open one or both cameras. Check connections or indices.")
        exit(1)

    # Create StereoSGBM object for disparity computation
    # Alternative: Use StereoBM with `stereo = cv2.StereoBM_create(numDisparities=64, blockSize=15)`
    stereo = cv2.StereoSGBM_create(
        minDisparity=0,           # Minimum disparity value
        numDisparities=64,        # Number of disparities to consider (must be divisible by 16)
        blockSize=7,              # Block size for matching (odd number)
        P1=8 * 3 * 7**2,         # Penalty on disparity change by 1
        P2=32 * 3 * 7**2,        # Penalty on disparity change by more than 1
        disp12MaxDiff=1,          # Maximum allowed difference in disparity check
        uniquenessRatio=10,       # Margin in % by which the best match should be better
        speckleWindowSize=100,    # Maximum size of smooth disparity regions
        speckleRange=32,          # Maximum disparity variation within each region
        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY  # Use 3-way tree for better accuracy
    )

    # Variables for FPS calculation
    prev_time = time.time()
    frame_count = 0
    fps = 0.0

    try:
        while True:
            # Start timing for FPS
            start_time = time.time()

            # Capture frames from both cameras
            ret_left, frame_left = cap_left.read()
            ret_right, frame_right = cap_right.read()

            if not ret_left or not ret_right:
                print("Error capturing frames")
                break

            # Convert frames to grayscale for disparity computation
            gray_left = cv2.cvtColor(frame_left, cv2.COLOR_BGR2GRAY)
            gray_right = cv2.cvtColor(frame_right, cv2.COLOR_BGR2GRAY)

            # Compute disparity map
            disparity = stereo.compute(gray_left, gray_right).astype(np.float32) / 16.0

            # Normalize disparity for display (map to 0-255 range)
            disparity_normalized = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

            # Combine original frames side by side for display
            combined_frame = np.hstack((frame_left, frame_right))

            # Display the combined frame and disparity map
            cv2.imshow('Stereo Vision', combined_frame)
            cv2.imshow('Disparity Map', disparity_normalized)

            # Calculate FPS
            frame_count += 1
            current_time = time.time()
            frame_time = current_time - start_time
            if frame_time > 0:
                fps = 1.0 / frame_time
            # Print FPS every frame
            print(f"FPS: {fps:.2f}")

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Release resources
        cap_left.release()
        cap_right.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Starting stereo vision capture with depth estimation and FPS display...")
    capture_stereo_vision_with_depth()
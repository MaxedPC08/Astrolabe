import cv2
import os

# Directory containing the images
directory = 'Coprocessor/images'

# Resize parameters
scale_percent = 30  # percent of original size

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):  # check if the file is an image
        # Read the image
        img = cv2.imread(os.path.join(directory, filename))
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (540, 960)
        # Resize the image
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

        # Save the resized image
        cv2.imwrite(os.path.join(directory, 'resized_' + filename), resized)
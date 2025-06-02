import cv2
import numpy as np

def sharp_img(frame):
    sharpen_kernel = np.array([
        [-1, -1, -1],
        [-1,  9, -1],
        [-1, -1, -1]
    ])
    # Asumsikan input frame dalam format BGR
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    sharpened = cv2.filter2D(img_rgb, -1, sharpen_kernel)
    return sharpened  # output dalam RGB
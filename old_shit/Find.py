import numpy as np
import cv2
from time import time


def Reduce_image(scr, scale_percent=25):
    width = int(scr.shape[1] * scale_percent / 100)
    height = int(scr.shape[0] * scale_percent / 100)
    dsize = (width, height)
    return cv2.resize(scr, dsize)


image = cv2.imread("Screenshot_red_106.png")
r, g, b = cv2.split(Reduce_image(image))
mask_image = r == 255
cv2.imwrite(f"Test/00000.png", r)

ts = time()

seg_0 = []
inf_seg_0 = []
p = True
up_seg = 0
for y in range(0, 125):
    if max(mask_image[y, :]) and p:
        up_seg = y
        p = False
    elif not max(mask_image[y, :]) and not p:
        seg_0.append(mask_image[up_seg:y, :])
        inf_seg_0.append([up_seg, y])
        p = True

segments = []
inf_segments = []
for s in range(0, len(seg_0)):
    p = True
    left_seg = 0
    for x in range(0, 187):
        if max(seg_0[s][:, x]) and p:
            left_seg = x
            p = False
        elif not max(seg_0[s][:, x]) and not p:
            segments.append(seg_0[s][:, left_seg:x])
            inf_segments.append([inf_seg_0[s][0], left_seg, inf_seg_0[s][1], x])
            p = True

print(time() - ts)

for j in range(0, len(segments)):
    segment = segments[j]
    color_object_image = segment.astype(np.uint8)
    color_object_image *= 255
    cv2.imwrite(f"Test/{j}.png", color_object_image)

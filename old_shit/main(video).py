from threading import Thread
import dxcam
import keyboard as key
from time import sleep, time
import cv2
import numpy as np
import os
import datetime
import ctypes
from random import random
import yaml
from ctypes import *

i = 0


def find_or_create_file(path):
    try:
        os.mkdir(path)
    except IOError:
        return False


# Creating constants and variables
width_screen, height_screen = windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1)

path = os.path.abspath(__file__).replace('\\', '/')
path = path[:path.rfind("/")]
t = str(datetime.datetime.now()).replace(':', '-')

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)
Video_write = config["Video_write"]
Log_write = config["Log_write"]
Fragments_write = config["Fragments_write"]
fps = 10 if Video_write else config["fps"]
scale_percent = config["scale_percent"]

if Fragments_write:
    find_or_create_file(f'{path}/Screenshots')
    os.mkdir(f'{path}/Screenshots/{t}')
    os.mkdir(f'{path}/Screenshots/{t}/Up')
    os.mkdir(f'{path}/Screenshots/{t}/Left')
    os.mkdir(f'{path}/Screenshots/{t}/Right')
    os.mkdir(f'{path}/Screenshots/{t}/GB')
    os.mkdir(f'{path}/Screenshots/{t}/Other')
if Log_write:
    find_or_create_file(f'{path}/Logs')
    Log = open(f"Logs/Log {t}.txt", "w")
if Video_write:
    find_or_create_file(f'{path}/Screen_recording')
    os.mkdir(f'{path}/Screen_recording/{t}')
    Video = cv2.VideoWriter(f'{path}/Screen_recording/{t}/Video{i}.mp4', cv2.VideoWriter_fourcc(*"mp4v"), fps, (width_screen, height_screen))


# Creating functions
def none():
    return None


def tap(k):
    key.press(k)
    sleep(random() / 10)
    key.release(k)


def Reduce_image(scr):
    global scale_percent
    width = int(scr.shape[1] * scale_percent / 100)
    height = int(scr.shape[0] * scale_percent / 100)
    dsize = (width, height)
    return cv2.resize(scr, dsize)


def is_capslock_on():
    return True if ctypes.WinDLL("User32.dll").GetKeyState(0x14) else False


def wait_white(region):
    global screenshot, Video_write
    find = False
    t_s = time()
    while not find and time() - t_s < 2:
        r, g, b = cv2.split(Reduce_image(screenshot[region[0]:region[2], region[1]:region[3]]))
        b_color = ((r == 255) * (b > 245) * (g > 245))
        if b_color.any():
            find = True
            tap("K")
            if Video_write:
                cv2.putText(screenshot, "K", (region[0] - (region[0] - region[2]) // 2, region[1] - (region[1] - region[3]) // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        while time() - t_s < 1 / fps:
            sleep(0.0001)


def find_left(image, width_image, height_image):
    su = 0
    for y in range(0, height_image):
        for x in range(0, width_image):
            if image[y, x]:
                if y * width_image > x * height_image:
                    su += 1
                elif y * width_image < x * height_image:
                    su -= 1
    if su > 10:
        return True
    else:
        return False


def find_right(image, width_image, height_image):
    su = 0
    for y in range(0, height_image):
        for x in range(0, width_image):
            if image[y, x]:
                if y * width_image > (width_image - x) * height_image:
                    su += 1
                elif y * width_image < (width_image - x) * height_image:
                    su -= 1
    if su > 10:
        return True
    else:
        return False


def circle_and_sign(region_circle, text=""):
    global screenshot
    cv2.rectangle(screenshot, (region_circle[1], region_circle[0]),
                  (region_circle[3], region_circle[2]), (255, 0, 0), 5)
    cv2.putText(screenshot, text, (region_circle[1], region_circle[2] + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (255, 0, 0), 2)


def Recording():  # Доделать
    global fps, screenshot, Video, b_rec
    while True:
        while b_rec:
            sleep(1/fps)
            Video.write(screenshot)


th_up = Thread(target=none())
th_left = Thread(target=none())
th_right = Thread(target=none())

key.wait("Caps Lock")
camera = dxcam.create()
camera.start(video_mode=True, target_fps=fps)
REGION = [height_screen // 4, width_screen // 4, height_screen // 4 * 3, width_screen // 4 * 3]

if Log_write:
    Log.write(f"Screen resolution: {width_screen}*{height_screen}. Search region:{REGION}\n")

main_process = False
while True:
    if Video_write and main_process:
        b_rec = True
        rec = Thread(target=Recording)
        rec.start()

    while is_capslock_on():
        main_process = True
        time_start = time()
        screenshot = camera.get_latest_frame()
        screenshot_0 = screenshot[REGION[0]:REGION[2], REGION[1]:REGION[3]]
        r, g, b = cv2.split(Reduce_image(screenshot_0))
        if Video_write:
            circle_and_sign(REGION, text=f"Finding Region. Size: {REGION[2] - REGION[0]}*{REGION[3] - REGION[1]}")

        r, g, b = r >> 2, g >> 2, b >> 2
        mask_image = r - 35 - b - g < 64

        seg_0 = []
        inf_seg_0 = []
        p = True
        up_seg = 0
        for y in range(0, int((REGION[2] - REGION[0]) / 100 * scale_percent)):
            if max(mask_image[y,:]) and p:
                up_seg = y
                p = False
            elif not max(mask_image[y,:]) and not p:
                seg_0.append(mask_image[up_seg:y,:])
                inf_seg_0.append([up_seg, y])
                p = True

        segments = []
        inf_segments = []
        for s in range(0, len(seg_0)):
            p = True
            left_seg = 0
            for x in range(0, int((REGION[3] - REGION[1]) / 100 * scale_percent)):
                if max(seg_0[s][:, x]) and p:
                    left_seg = x
                    p = False
                elif not max(seg_0[s][:, x]) and not p:
                    segments.append(seg_0[s][:, left_seg:x])
                    inf_segments.append([inf_seg_0[s][0], left_seg, inf_seg_0[s][1], x])
                    p = True

        for j in range(0, len(segments)):
            segment = segments[j]
            for ind in range(0, 4):
                inf_segments[j][ind] = int(inf_segments[j][ind] / scale_percent * 100)
            up, left, down, right = inf_segments[j]
            height_image, width_image = segment.shape[0], segment.shape[1]
            type_object = "Other"

            if height_image > (height_screen / 500) and width_image > (width_screen / 500):  # Допилить
#                if width_image < height_image <= 15:  # Допилить
#                    parry_GB = Thread(target=tap, args="M")
#                    parry_GB.start()
#                    type_object = "GB"
                if width_image > height_image * 1.3:  # Допилить
                    parry_up = Thread(target=tap, args="I")
                    parry_up.start()
                    type_object = "Up"
                    new_region = [REGION[0] + up - 200, REGION[1] + left - 50, REGION[0] + down, REGION[1] + right + 100]
                    if not th_up.is_alive():
                        th_up = Thread(target=wait_white, args=(new_region,))
                        th_up.start()
                elif width_image * 1.2 < height_image and find_left(segment, width_image, height_image):  # Допилить
                    parry_left = Thread(target=tap, args="J")
                    parry_left.start()
                    type_object = "Left"
                    new_region = [REGION[0] + up - 50, REGION[1] + left - 50, REGION[0] + down + 150, REGION[1] + right + 100]
                    if not th_left.is_alive():
                        th_left = Thread(target=wait_white, args=(new_region,))
                        th_left.start()
                elif width_image * 1.2 < height_image and find_right(segment, width_image, height_image):  # Допилить
                    parry_right = Thread(target=tap, args="L")
                    parry_right.start()
                    type_object = "Right"
                    new_region = [REGION[0] + up - 50, REGION[1] + left - 50, REGION[0] + down + 150, REGION[1] + right + 100]
                    if not th_right.is_alive():
                        th_right = Thread(target=wait_white, args=(new_region,))
                        th_right.start()

                if Video_write and (type_object == "GB" or type_object == "Up" or type_object == "Left" or type_object == "Right"):
                    circle_and_sign(new_region, text=f"{type_object} find. Size: {new_region[2] - new_region[0]}*{new_region[3] - new_region[1]}")

            if Log_write:
                Log.write(
                    f"An object of the type {type_object} number {i}_{j} has been found. Region: {REGION[0] + left} {REGION[1] + up} {right - left} {down - up}\n")

            if Fragments_write:
                color_object_image = segment.astype(np.uint8)
                color_object_image *= 255
                cv2.imwrite(f'Screenshots/{t}/{type_object}/Screenshot_red_{i}_{j}.png', color_object_image)

        if Fragments_write:
            color_object_image = mask_image.astype(np.uint8)
            color_object_image *= 255
            cv2.imwrite(f'Screenshots/{t}/Mask_{i}.png', color_object_image)
        time_end = time()
        while time() - time_start < 1 / fps:
            sleep(0.0001)

        print(i, time_end - time_start)
        i += 1

    main_process = False
    if Video_write:
        b_rec = False
        Video.release()
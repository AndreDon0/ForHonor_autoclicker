from threading import Thread
import dxcam
import keyboard as key
import pyautogui as pag
from time import sleep
from time import time
import cv2
import numpy as np
import os
import datetime
from os.path import abspath
import ctypes
from random import random
import yaml


def none():
    return None


def tap(k):
    key.press(k)
    sleep(random() / 50)
    key.release(k)


def take_screen(scr_region=[0, 0, pag.size()[0], pag.size()[1]]):
    scr = camera.get_latest_frame()
    scr = scr[scr_region[1]:scr_region[1] + scr_region[3], scr_region[0]:scr_region[0] + scr_region[2]]
    return scr


def is_capslock_on():
    return True if ctypes.WinDLL("User32.dll").GetKeyState(0x14) else False


def find_or_create_file(path):
    try:
        os.mkdir(path)
    except IOError:
        return False


def wait_white(region_white):
    p_white = 0
    te_white = 0
    ts_white = time()
    while p_white == 0 and te_white - ts_white < 1.5:
        if Video_write_mode:
            r_white, g_white, b_white = cv2.split(screenshot(region_white))
        else:
            r_white, g_white, b_white = cv2.split(take_screen(region_white))
        for y_white in range(0, region_white[3], 8):
            for x_white in range(0, region_white[2], 8):
                if r_white[y_white, x_white] > 250 and 210 < b_white[y_white, x_white] < 230 and 210 < g_white[y_white, x_white] < 230:
                    p_white = 1
        te_white = time()
    if p_white > 0:
        attask = Thread(target=tap, args="K", daemon=True)
        attask.start()
        sleep(0.4)


def find_left(image, width_image, height_image):
    su = 0
    for y in range(0, height_image):
        for x in range(0, width_image):
            if image[y, x] == 255:
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
            if image[y, x] == 255:
                if y * width_image > (width_image - x) * height_image:
                    su += 1
                elif y * width_image < (width_image - x) * height_image:
                    su -= 1
    if su > 10:
        return True
    else:
        return False


def circle_and_sign(region_circle, text=""):
    global video_fragment
    cv2.rectangle(video_fragment, (region_circle[0], region_circle[1]),
                  (region_circle[0] + region_circle[2], region_circle[1] + region_circle[3]), (0, 0, 255), 5)
    cv2.putText(video_fragment, text, (region_circle[0], region_circle[1] + region_circle[3] + 20), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (255, 255, 255), 2)


def Recording():
    global fps, width, height
    global screenshot, video_fragment, video
    while True:
        time_start = time()
        while circle_main_region.is_alive():
            pass
        try:
            video.write(video_fragment)
        except cv2.error:
            pass
        screenshot = camera.get_latest_frame()
        video_fragment = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        while time() - time_start < 1 / fps:
            pass


path = abspath(__file__).replace('\\', '/')
path = path[:path.rfind("/")]
t = str(datetime.datetime.now()).replace(':', '-')

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)
fps = config["fps"]
Video_write_mode = config["Video_write_mode"]
Log_write = config["Log_write"]
Fragments_write = config["Fragments_write"]

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
if Video_write_mode:
    find_or_create_file(f'{path}/Screen_recording')
    os.mkdir(f'{path}/Screen_recording/{t}')

th_up = Thread(target=none())
th_left = Thread(target=none())
th_right = Thread(target=none())

key.wait("Caps Lock")
if Video_write_mode and fps > 20:
    fps = 20
camera = dxcam.create()
camera.start(video_mode=True, target_fps=fps)
width, height = pag.size()
REGION = [width // 9 * 4, height // 3, width // 6, height // 4]  # Допилить
if Log_write:
    Log.write(f"Screen resolution: {width}*{height}. Search region:{REGION}\n")
if Video_write_mode:
    video = cv2.VideoWriter(f'{path}/Screen_recording/{t}/Video.mp4', cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    screenshot = camera.get_latest_frame()
    video_fragment = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
    circle_main_region = Thread(target=circle_and_sign, args=(REGION, "Finding Region"), daemon=True)
    rec = Thread(target=Recording, args=(), daemon=True)
    rec.start()
i = 1

while True:
    camera.stop()
    if is_capslock_on():
        camera.start(video_mode=True, target_fps=fps)
    while is_capslock_on():
        time_start = time()
        if Video_write_mode:
            r, g, b = cv2.split(screenshot[REGION[1]:REGION[1] + REGION[3], REGION[0]:REGION[0] + REGION[2]])
            circle_main_region = Thread(target=circle_and_sign, args=(REGION, "Finding Region"), daemon=True)
        else:
            r, g, b = cv2.split(take_screen(REGION))
        r, g, b = r >> 2, g >> 2, b >> 2
        up = REGION[3]
        down = 0
        left = REGION[2]
        right = 0
        for y in range(0, REGION[3], 4):
            for x in range(0, REGION[2], 4):
                if r[y, x] < 35 + b[y, x] + g[y, x] * 2:
                    r[y // 4, x // 4] = 0
                else:
                    r[y // 4, x // 4] = 255
                    if y > down:
                        down = y
                    if y < up:
                        up = y
                    if x < left:
                        left = x
                    if x > right:
                        right = x
        image = r[up // 4:down // 4, left // 4:right // 4]
        width_image, height_image = image.shape[1], image.shape[0]
        tipe_object = ""
        if width / 220 < width_image < width / 64 and height / 200 < height_image < height / 40:
            if Log_write:
                Log.write(
                    f"An object has been found. Region: {REGION[0] + left} {REGION[1] + up} {right - left} {down - up}\n")
            if width_image < height_image <= width_image + int(width / 640) <= 15:
                parry_GB = Thread(target=tap, args="M", daemon=True)
                parry_GB.start()
                tipe_object = "GB"
                sleep(0.2)
            elif width_image > height_image * 1.3:
                parry_up = Thread(target=tap, args="I", daemon=True)
                parry_up.start()
                tipe_object = "Up"
                new_region = [REGION[0] + left - 50, REGION[1] + up - 100, right - left + 100, down - up + 50]
                if not th_up.is_alive():
                    th_up = Thread(target=wait_white, args=[new_region], daemon=True)
                    th_up.start()
            elif width_image * 1.2 < height_image and find_left(image, width_image, height_image):
                parry_left = Thread(target=tap, args="J", daemon=True)
                parry_left.start()
                tipe_object = "Left"
                new_region = [REGION[0] + left - 50, REGION[1] + up - 50, right - left + 100, down - up + 150]
                if not th_left.is_alive():
                    th_left = Thread(target=wait_white, args=[new_region], daemon=True)
                    th_left.start()
            elif width_image * 1.2 < height_image and find_right(image, width_image, height_image):
                parry_right = Thread(target=tap, args="L", daemon=True)
                parry_right.start()
                tipe_object = "Right"
                new_region = [REGION[0] + left - 50, REGION[1] + up - 50, right - left + 100, down - up + 150]
                if not th_right.is_alive():
                    th_right = Thread(target=wait_white, args=[new_region], daemon=True)
                    th_right.start()
            else:
                tipe_object = "Other"
        elif width_image > 0 and height_image > 0:
            tipe_object = "Other"

        if Fragments_write and tipe_object != "":
            cv2.imwrite(f'Screenshots/{t}/{tipe_object}/Screenshot_red_{i}.png', image)

        while time() - time_start < 0.1:
            sleep(0.01)
        time_end = time()
        i += 1
        print(i, time_end - time_start)
    if Video_write_mode:
        video.release()

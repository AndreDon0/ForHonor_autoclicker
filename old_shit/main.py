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


def take_screen(scr_region):
    while True:
        scr = camera.grab(region=(scr_region[0], scr_region[1], scr_region[0] + scr_region[2], scr_region[1] + scr_region[3]))
        if scr is not None:
            return cv2.split(scr)


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
        r_white, g_white, b_white = take_screen(region_white)
        # r_white = r_white[::8,::8]
        # g_white = g_white[::8,::8]
        # b_white = b_white[::8,::8]
        # mask = (r_white > 250) & (210 < b_white) & (b_white > 230) & (210 < g_white) & (g_white < 230)
        # p_white = mask.sum()
        for y_white in range(0, region_white[3], 8):
            for x_white in range(0, region_white[2], 8):
                if r_white[y_white, x_white] > 250 and 210 < b_white[y_white, x_white] < 230 and 210 < g_white[y_white, x_white] < 230:
                    p_white = 1
        te_white = time()
    if p_white > 0:
        attask = Thread(target=tap("K"))
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


path = abspath(__file__).replace('\\', '/')
path = path[:path.rfind("/")]
t = str(datetime.datetime.now()).replace(':', '-')
find_or_create_file(f'{path}/Screenshots')
find_or_create_file(f'{path}/Logs')

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)
fps = config["fps"]

os.mkdir(f'{path}/Screenshots/{t}')
os.mkdir(f'{path}/Screenshots/{t}/Up')
os.mkdir(f'{path}/Screenshots/{t}/Left')
os.mkdir(f'{path}/Screenshots/{t}/Right')
os.mkdir(f'{path}/Screenshots/{t}/GB')
os.mkdir(f'{path}/Screenshots/{t}/Other')
Log = open(f"Logs/Log {t}.txt", "w")
th_up = Thread(target=none())
th_left = Thread(target=none())
th_right = Thread(target=none())

key.wait("Caps Lock")
camera = dxcam.create()
width, height = pag.size()
REGION = [int(width/2.25), int(height/3), int(width/6), int(height/4)]  # Допилить
Log.write(f"Screen resolution: {width}*{height}. Search region:{REGION}\n")
i = 1
while True:
    while is_capslock_on():
        time_start = time()
        r, g, b = take_screen(REGION)
        r, g, b = np.array(r, np.int16), np.array(g, np.int16), np.array(b, np.int16)
        up = REGION[3]
        down = 0
        left = REGION[2]
        right = 0
        for y in range(0, REGION[3], 4):
            for x in range(0, REGION[2], 4):
                if r[y, x] - b[y, x] - g[y, x] * 2 < 140:
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
        if width / 220 < width_image < width / 64 and height / 200 < height_image < height / 40:
            Log.write(f"An object has been found. Region: {REGION[0] + left} {REGION[1] + up} {right - left} {down - up}\n")
            image = np.array(image, np.uint8)
            if width_image < height_image <= width_image + int(width / 640) <= 15:
                cv2.imwrite(f'Screenshots/{t}/GB/Screenshot_red_{i}.png', image)
                parry_GB = Thread(target=tap("M"))
                sleep(0.2)
            elif width_image > height_image * 1.3:
                parry_up = Thread(target=tap("I"))
                new_region = [REGION[0] + left - 50, REGION[1] + up - 100, right - left + 100,
                              down - up + 50]
                cv2.imwrite(f'Screenshots/{t}/Up/Screenshot_red_{i}.png', image)
                if not th_up.is_alive():
                    th_up = Thread(target=wait_white(new_region))
            elif width_image * 1.2 < height_image and find_left(image, width_image, height_image):
                parry_left = Thread(target=tap("J"))
                new_region = [REGION[0] + left - 50, REGION[1] + up - 50, right - left + 100,
                              down - up + 150]
                cv2.imwrite(f'Screenshots/{t}/Left/Screenshot_red_{i}.png', image)
                if not th_left.is_alive():
                    th_left = Thread(target=wait_white(new_region))
            elif width_image * 1.2 < height_image and find_right(image, width_image, height_image):
                parry_right = Thread(target=tap("L"))
                new_region = [REGION[0] + left - 50, REGION[1] + up - 50, right - left + 100,
                              down - up + 150]
                cv2.imwrite(f'Screenshots/{t}/Right/Screenshot_red_{i}.png', image)
                if not th_right.is_alive():
                    th_right = Thread(target=wait_white(new_region))
            else:
                cv2.imwrite(f'Screenshots/{t}/Other/Screenshot_red_{i}.png', image)
        elif width_image > 0 and height_image > 0:
            cv2.imwrite(f'Screenshots/{t}/Other/Screenshot_red_{i}.png', image)

        while time() - time_start < 0.1:
            sleep(0.01)
        time_end = time()
        i += 1
        print(i, time_end - time_start)

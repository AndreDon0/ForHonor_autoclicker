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


def take_screen(scr_region):
    try:
        r, b, g = cv2.split(camera.grab(
            region=(scr_region[0], scr_region[1], scr_region[0] + scr_region[2], scr_region[1] + scr_region[3])))
        return r, b, g
    except ValueError:
        return take_screen(scr_region)


def is_capslock_on():
    return True if ctypes.WinDLL("User32.dll").GetKeyState(0x14) else False


key.wait("Caps Lock")
camera = dxcam.create()
width, height = pag.size()
REGION = [750, 300, 500, 500]

try:
    f = open('Settings.txt', "r")
    file = f.read()
    fps = int(file[file.find("fps=")+4:file.find("\n")])
except IOError:
    f = open('Settings.txt', 'w')
    f.write("fps=60\n")
    f.close()
    fps = 60

while True:
    while is_capslock_on():
        r, g, b = take_screen(REGION)
        r, g, b = np.array(r, np.int16), np.array(g, np.int16), np.array(b, np.int16)
        examination = False
        up = REGION[3]
        down = 0
        left = REGION[2]
        right = 0
        for y in range(0, REGION[3], 8):
            for x in range(0, REGION[2], 8):
                if r[y, x] > 210 and b[y, x] > 90 and g[y, x] > 90 and r[y, x] < 230 and b[y, x] < 110 and g[y, x] < 110:
                    r[y // 4, x // 4] = 0
                else:
                    examination = True
                    r[y // 4, x // 4] = 255
                    if y > down:
                        down = y
                    if y < up:
                        up = y
                    if x < left:
                        left = x
                    if x > right:
                        right = x
        image = r[up // 8:down // 8, left // 8:right // 8]
        width_image, height_image = image.shape[1], image.shape[0]
        if (width_image > 5 and height_image > 5) and (width_image < 30 or height_image > 30):
            key.press("A")
            sleep(1 / fps + 0.003)
            key.press("space")
            sleep(0.3)
            key.release("A")
            key.release("space")
            sleep(1)
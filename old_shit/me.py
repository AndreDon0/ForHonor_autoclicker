import keyboard as key
import pyautogui as pag
from time import sleep
from time import time
import cv2
import numpy as np
import os
import datetime


def find_GB(image, width_image, height_image):
    su = 0
    for x in range(0, width_image):
        p = 0
        if width_image / 2 > x:
            p = 1
        elif width_image / 2 < x:
            p = -1
        for y in range(0, height_image):
            if image[y, x] == 255:
                su += p
    if abs(su) < 15:
        return True
    else:
        return False


width, height = pag.size()
REGION = [width // 8 + 130, height // 4 + 320, 450, 450]
t = str(datetime.datetime.now()).replace(':', '-')
os.mkdir('C:/Users/andre/PycharmProjects/For honor/Screenshots/me' + t)

key.wait("insert")
while key.is_pressed("insert"):
    sleep(0.01)

while not key.is_pressed("insert"):
    screenshot = np.array(pag.screenshot(region=REGION))
    cv2.imwrite('Screenshots/me' + t + '.png', cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR))
    sleep(0.2)


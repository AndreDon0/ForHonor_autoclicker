import keyboard as key
import pyautogui as pag
from time import sleep
from time import time
import cv2
import numpy as np
import os
import datetime
key.wait("insert")
while key.is_pressed("insert"):
    continue
width, height = pag.size()
i = 1
while not key.is_pressed("insert"):
    REGION = [750, 300, 500, 500]
    screenshot = np.array(pag.screenshot(region=REGION))
    r, g, b = cv2.split(screenshot)
    cv2.imwrite('Screenshots/Screenshot'+ str(i) + '.png', cv2.merge([b, g, r]))
    i += 1
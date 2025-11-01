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


def tap(k1, k2=None):
    key.press(k1)
    if k2 is not None:
        key.press(k2)
    sleep(random() / 50)
    if k2 is not None:
        key.release(k2)
    key.release(k1)


def up():
    tap("I")

def left():
    tap("J")

def right():
    tap("L")

def parry():
    tap("K")

def gb():
    tap("M")

def bash():
    if random() < 0.5:
        tap("D", "space")
    else:
        tap("A", "space")


import keyboard
from time import sleep
from random import random
from threading import Thread

def tap(key_str):
    keyboard.press(key_str)
    sleep(random() / 50)
    keyboard.release(key_str)

def tap_thread(key_str):
    Thread(target=tap, args=(key_str,), daemon=True).start()

def up():
    tap_thread("I")

def left():
    tap_thread("J")

def right():
    tap_thread("L")

def parry():
    tap_thread("K")

def gb():
    tap_thread("H")

def bash():
    key = "D" if random() < 0.5 else "A"
    tap_thread(key)
    tap_thread("space")

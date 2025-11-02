import mss
import numpy as np
from ultralytics import YOLO
import ctypes
import time
import cv2
import torch
from actions import left, right, up, bash, parry, gb

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load YOLO model
model_path = "./best.pt"
model = YOLO(model_path)
model.to(DEVICE)
print(f"Model loaded successfully! Running on {DEVICE}.")

# --- Helper ---
def is_capslock_on():
    return True if ctypes.WinDLL("User32.dll").GetKeyState(0x14) else False

print("Waiting for Caps Lock to be on... Do it only in game!")
while not is_capslock_on():
    time.sleep(0.5)

# Setup screen region (same as before)
with mss.mss() as sct:
    monitor = sct.monitors[1]
    screen_width = monitor["width"]
    screen_height = monitor["height"]

x = screen_width // 4
y = screen_height // 4
width = screen_width // 2
height = screen_height // 2
capture_region = {"top": y, "left": x, "width": width, "height": height}

print(f"Capture region: {x},{y} to {x+width},{y+height} ({width}x{height})")

# --- Main loop ---

time.sleep(0.3)  # small delay to avoid instant re-trigger

while True:
    with mss.mss() as sct:
        while is_capslock_on():

            # Capture frame
            screenshot = sct.grab(capture_region)
            img_np = np.array(screenshot)
            img_np = img_np[:, :, :3]
            img_resized = cv2.resize(img_np, (100, 100), interpolation=cv2.INTER_LANCZOS4)

            # Detect
            results = model.predict(source=img_np, verbose=False)
            if len(results) > 0 and len(results[0].boxes) > 0:
                names = model.names
                counts = {}
                for c in results[0].boxes.cls.cpu().numpy().astype(int):
                    name = names[c]
                    if name == 'l0' or name == 'r0' or name == 'u0':
                        parry()
                    elif name == 'l':
                        left()
                    elif name == 'r':
                        right()
                    elif name == 'u':
                        up()
                    elif name == 'gb':
                        gb()
                    elif name == 'bash':
                        pass
                    counts[name] = counts.get(name, 0) + 1
                print("Detected:", counts)

            time.sleep(0.05)
        time.sleep(0.1)

import mss
import mss.tools
import os
from datetime import datetime
import time
import signal
import sys
from PIL import Image

# Create timestamped folder for screenshots
folder_name = datetime.now().strftime("screenshots/%Y-%m-%d_%H-%M-%S")

os.makedirs(folder_name, exist_ok=True)
print(f"Saving screenshots to: {folder_name}")

# Get screen dimensions
with mss.mss() as sct:
    monitor = sct.monitors[1]  # Primary monitor
    screen_width = monitor["width"]
    screen_height = monitor["height"]

# Define capture region (center half of screen)
x = screen_width // 4
y = screen_height // 4
width = screen_width // 2
height = screen_height // 2

capture_region = {
    "top": y,
    "left": x, 
    "width": width,
    "height": height
}

print(f"Screen: {screen_width}x{screen_height}")
print(f"Capture region: {x},{y} to {x+width},{y+height} ({width}x{height})")

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("\nShutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

frame_count = 0
start_time = time.time()
failed_captures = 0

print("Starting screenshot capture. Press Ctrl+C to stop.")

try:
    with mss.mss() as sct:
        while True:
            try:
                # Capture screen
                screenshot = sct.grab(capture_region)
                
                if screenshot:
                    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                    img = img.resize((100, 100), Image.Resampling.LANCZOS)
                
                    filename = os.path.join(folder_name, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{frame_count:06d}.png")
                    img.save(filename, "PNG")
                    
                    frame_count += 1
                    failed_captures = 0
                    
                    # Print status every 30 frames
                    if frame_count % 30 == 0:
                        elapsed = time.time() - start_time
                        fps = frame_count / elapsed
                        print(f"Frames: {frame_count}, FPS: {fps:.2f}, Time: {elapsed:.1f}s")
                
            except Exception as e:
                failed_captures += 1
                print(f"Capture error: {e}")
                if failed_captures > 5:
                    print("Too many failed captures, exiting...")
                    break
                time.sleep(0.1)

except KeyboardInterrupt:
    print("\nCapture interrupted by user")

except Exception as e:
    print(f"Unexpected error: {e}")

finally:
    total_time = time.time() - start_time
    print(f"\nCapture completed!")
    print(f"Total frames: {frame_count}")
    print(f"Total time: {total_time:.2f}s")
    if total_time > 0 and frame_count > 0:
        print(f"Average FPS: {frame_count/total_time:.2f}")
    print(f"Screenshots saved to: {folder_name}")


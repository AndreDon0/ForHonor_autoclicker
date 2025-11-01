import torch
import mss
import numpy as np
from PIL import Image

# Load your PyTorch model
model_path = "./data_split/best.pt"
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading model from {model_path} on {device}...")
model = torch.load(model_path, map_location=device)
model.eval()
print("Model loaded and ready.")

# Get screen info
with mss.mss() as sct:
    monitor = sct.monitors[1]
    screen_width = monitor["width"]
    screen_height = monitor["height"]

# Define capture region (same as your recording code)
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

print(f"Capture region: {x},{y} to {x+width},{y+height} ({width}x{height})")

# Main loop
with mss.mss() as sct:
    while True:
        # Grab screenshot
        screenshot = sct.grab(capture_region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        img = img.resize((100, 100), Image.Resampling.LANCZOS)

        # Convert image to tensor
        img_tensor = torch.from_numpy(np.array(img)).float().permute(2, 0, 1) / 255.0
        img_tensor = img_tensor.unsqueeze(0).to(device)

        # Inference
        with torch.no_grad():
            output = model(img_tensor)

        # Process output depending on model type
        # (Example assumes model returns dict with 'boxes', 'labels', 'scores')
        if isinstance(output, (list, tuple)):
            output = output[0]

        if isinstance(output, dict) and "labels" in output:
            labels = output["labels"].cpu().numpy()
            # You may have a mapping of class names:
            # class_names = ['person', 'car', 'dog', ...]
            # Example placeholder:
            class_names = [f"class_{i}" for i in range(100)]
            counts = {}
            for lbl in labels:
                name = class_names[lbl] if lbl < len(class_names) else str(lbl)
                counts[name] = counts.get(name, 0) + 1

            print("Detected objects:", counts if counts else "None")

        else:
            print("Model output format not recognized:", type(output))

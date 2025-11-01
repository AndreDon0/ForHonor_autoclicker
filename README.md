
# Fast Center Half Screen Recorder

This Python script captures the center half of your Windows screen at high speed using `dxcam`, saving all screenshots to a timestamped folder and displaying live preview with FPS shown in the terminal.

## Setup

1. Install dependencies:

```
pip install -r requirements.txt
```

## Usage

Run the script:

```
python your_script_name.py
```

- A new folder named by the current timestamp will be created.
- Captured frames will be saved as PNG images inside that folder.
- The live preview window shows the captured region.
- The terminal displays the current frames per second (FPS) every 30 frames.
- Press `q` in the preview window to stop recording.

---

Make sure you run this on Windows 10 or newer for best performance with `dxcam`.

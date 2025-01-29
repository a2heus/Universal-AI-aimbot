# AI Aimbot

## Description
This project is for educational purposes and demonstrates the use of AI for real-time object tracking. It utilizes a YOLOv5 model to detect targets on the screen and an algorithm to move the mouse smoothly and predictably towards the detected target.

> **Warning:** This project is intended solely for educational and experimental purposes. Any use for unethical or illegal activities is strictly prohibited.

---

## Installation
Before running this project, ensure that you have installed all the required dependencies. You can install them using `pip`:

```bash
pip install torch torchvision numpy opencv-python dxcam pynput pyautogui
```

> **Note:** This project works only on Windows due to the use of `ctypes` and Windows-specific libraries.

---

## How It Works
1. **Model Initialization**: A pre-trained YOLOv5 model is loaded for object detection.
2. **Screen Capture**: The `dxcam` library is used to capture a specific region of the screen.
3. **Target Detection**: YOLOv5 identifies detected objects and selects the best candidate based on confidence and class.
4. **Mouse Movement**: The target's position is calculated, and interpolation is applied to move the mouse smoothly toward it.
5. **Activation via Right Click**: The tracking and movement algorithm activates only when the user holds down the right mouse button.
6. **Stopping and Closing**: The user can exit the program by pressing `q`.

---

## Variable Configuration
The program's behavior can be adjusted via several constants defined at the beginning of the script:

| Variable | Default Value | Description |
|----------|--------------|-------------|
| `TARGET_SMOOTHING` | `0.50` | Smooths the target to avoid abrupt movements. |
| `MIN_CONFIDENCE` | `0.45` | Minimum confidence for the model to consider a detection. |
| `LERP_SPEED` | `0.9` | Linear interpolation factor to smooth tracking. |
| `MAX_SPEED` | `1000` | Maximum speed of mouse movement. |
| `DECELERATION_RADIUS` | `50` | Deceleration radius around the target to prevent abrupt stops. |
| `STOPPING_THRESHOLD` | `3` | Distance in pixels below which the mouse stops moving. |
| `PREDICTIVE_FACTOR` | `0.1` | Prediction factor to compensate for target movement. |
| `INPUT_SAMPLE_RATE` | `0.001` | Sampling frequency for mouse movement. |

---

## Credits
- **YOLOv5**: Ultralytics ([GitHub](https://github.com/ultralytics/yolov5))
- **dxcam**: Fast screen capture for Windows
- **pynput**: Mouse input handling
- **ctypes**: Simulating mouse movements
- **OpenCV**: Real-time image processing
- **Pyautogui**: Screen Size
  
---

## Note
If you want to modify the capture region, adjust the `region` variable in the main script:
```python
w, h = pyautogui.size()
s = 500  # Capture region size
l = (w - s) // 2
t = (h - s) // 2
region = (l, t, l + s, t + s)
```

---

## Running the Project
Simply run the Python script:
```bash
python script.py
```

To stop the program, press `q` in the display window.

---

## License
This project is provided for educational purposes only. Using this code for any illegal activities is strictly prohibited.


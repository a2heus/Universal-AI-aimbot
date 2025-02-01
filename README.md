# Universal AI Aimbot

![Demo](https://streamable.com/z8hv7h)

> **Disclaimer:**  
> This project is intended for educational and experimental purposes only. The author is not responsible for any misuse. Use this tool at your own risk and ensure you comply with all applicable laws and game terms of service.

---

## Overview

This project implements an aimbot that automatically detects targets on-screen and moves the mouse pointer smoothly to lock onto them. Built using Python, it leverages the power of a pre-trained YOLOv5 model for real-time object detection and utilizes screen capturing via `dxcam`. The aimbot is toggled using the right mouse button and provides visual feedback (bounding boxes, FPS, and target information) on an OpenCV window.

The code was developed by **a2heus**, a 16-year-old developer, as a personal project. It serves as a learning tool for computer vision and real-time processing.

---

## Features

- **Real-Time Object Detection:**  
  Utilizes a pre-trained YOLOv5 model (loaded via `torch.hub`) to detect objects in a defined screen region.
  
- **Screen Capture:**  
  Uses `dxcam` to capture a specified region of your screen for processing.
  
- **Smooth Mouse Movement:**  
  Calculates and applies smooth, gradual mouse movements to simulate aimbot functionality with configurable smoothness and head offset.
  
- **Target Locking:**  
  Automatically selects and locks onto the target closest to the center of the screen. It also maintains target tracking by checking proximity between frames.
  
- **Toggle Control:**  
  Activates or deactivates the aimbot using the right mouse button.
  
- **On-Screen Visual Feedback:**  
  Displays bounding boxes, confidence scores, FPS, and aimbot status on a window.

---

## Demo Video

Watch the demonstration of the aimbot in action:  
[Demo on Streamable](https://streamable.com/z8hv7h)

---

## Installation

### Prerequisites

- **Operating System:** Windows (the project uses Windows-specific libraries such as `win32api` and `dxcam`)
- **Python:** Version 3.8 or higher is recommended

### Required Python Libraries

Install the required dependencies via `pip`. You can create a virtual environment if desired.

```bash
pip install opencv-python torch numpy dxcam pynput pywin32
```

> **Note:**  
> The project uses the YOLOv5 model from Ultralytics, which will be automatically downloaded when running the code for the first time.

---

## Usage

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/a2heus/Universal-AI-aimbot.git
   cd aimbot-project
   ```

2. **Run the Program:**

   Simply execute the main Python file:

   ```bash
   python script.py
   ```

3. **Controls:**

   - **Right Mouse Button:** Hold down to enable the aimbot; release to disable.
   - **'q' Key:** Press to quit the application.

The program will open an OpenCV window displaying the processed video feed with:
- **Bounding Boxes:** Green for detected targets; red if the target is locked.
- **FPS Display**
- **Aimbot Status:** Shows whether the aimbot is enabled.
- **Target Information:** Displays the center coordinates and confidence score of the locked target.

---

## Configuration

The behavior of the aimbot can be adjusted by modifying the following global variables in the code:

- **`HEAD_OFFSET`**:  
  Adjusts the vertical offset for the aiming point.  
  - Negative values raise the target (aim higher).  
  - Positive values lower the target (aim lower).

- **`SMOOTHNESS`**:  
  Determines how gradual the mouse movement is.  
  - Lower values yield slower and smoother movement.

- **`TARGET_LOCK_THRESHOLD`**:  
  The maximum allowable distance (in pixels) between the previously locked target and a new detection for maintaining the lock.

These parameters are defined at the top of the source code and can be tweaked to suit your needs.

---

## How It Works

1. **Model Loading:**  
   The program loads the YOLOv5 model using `torch.hub` and sets a confidence threshold (`model.conf = 0.5`).

2. **Screen Capture:**  
   A screen region is defined (centered on the screen) and captured using `dxcam`.

3. **Target Detection:**  
   Each frame is processed by the YOLOv5 model. Detected targets of allowed classes are filtered by confidence and processed to compute their center positions.

4. **Target Locking & Mouse Movement:**  
   - The target closest to the center of the screen is selected as the "locked" target.
   - If the aimbot is enabled (via right mouse button), the program calculates the mouse movement required to reach the target’s position, applying a smooth transition.
   - The mouse is moved using Windows API functions.

5. **Display:**  
   Processed frames are displayed in a window with overlays indicating the current status, FPS, and target information.

---

## Dependencies and Resources

- **OpenCV:** [opencv.org](https://opencv.org/)
- **PyTorch:** [pytorch.org](https://pytorch.org/)
- **YOLOv5:** [Ultralytics YOLOv5 GitHub](https://github.com/ultralytics/yolov5)
- **dxcam:** [dxcam on PyPI](https://pypi.org/project/dxcam/)
- **pynput:** [pynput on PyPI](https://pypi.org/project/pynput/)
- **pywin32:** [pywin32 on PyPI](https://pypi.org/project/pywin32/)

---

## License

This project is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Acknowledgements

- Thanks to the developers of YOLOv5 and the Ultralytics team for providing an excellent object detection model.
- Special thanks to the maintainers of `dxcam`, `opencv-python`, and other libraries used in this project.
- Inspired by the possibilities of real-time computer vision and hardware control on Windows.

---

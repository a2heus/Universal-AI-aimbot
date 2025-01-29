import time
import torch
import cv2
import numpy as np
import dxcam
from pynput import mouse
import pyautogui
import ctypes
from ctypes import wintypes

# Configuration
TARGET_SMOOTHING = 0.50
MIN_CONFIDENCE = 0.45
LERP_SPEED = 0.9
MAX_SPEED = 1000
DECELERATION_RADIUS = 50
STOPPING_THRESHOLD = 3
PREDICTIVE_FACTOR = 0.1
INPUT_SAMPLE_RATE = 0.001

# Fix ULONG_PTR
if not hasattr(wintypes, 'ULONG_PTR'):
    ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
else:
    ULONG_PTR = wintypes.ULONG_PTR

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _anonymous_ = ["u"]
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", INPUT_UNION)
    ]

SendInput = ctypes.windll.user32.SendInput

def send_relative_mouse_move(dx, dy):
    inp = INPUT()
    inp.type = 0
    inp.mi = MOUSEINPUT(dx, dy, 0, 0x0001, 0, 0)
    SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

class TargetTracker:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.current_target = None
        self.last_target_time = 0
        self.active = False
        self.last_speed = (0.0, 0.0)

    def update_target(self, new_target):
        now = time.time()
        if new_target:
            if self.current_target:
                dx = new_target[0] - self.current_target[0]
                dy = new_target[1] - self.current_target[1]
                predicted_x = new_target[0] + dx * PREDICTIVE_FACTOR
                predicted_y = new_target[1] + dy * PREDICTIVE_FACTOR
                self.current_target = (
                    self.current_target[0] + (predicted_x - self.current_target[0]) * LERP_SPEED,
                    self.current_target[1] + (predicted_y - self.current_target[1]) * LERP_SPEED
                )
            else:
                self.current_target = new_target
            self.last_target_time = now
            self.active = True
        else:
            if now - self.last_target_time > 0.2:
                self.reset()

tracker = TargetTracker()
should_move = False

def on_click(x, y, button, pressed):
    global should_move
    if button == mouse.Button.right:
        should_move = pressed
        if pressed:
            tracker.reset()
            tracker.active = True
            update_actual_position(*pyautogui.position())
        else:
            tracker.reset()

def update_actual_position(x, y):
    global actual_x, actual_y
    actual_x, actual_y = x, y

def calculate_movement(current_pos, target_pos, dt):
    dx = target_pos[0] - current_pos[0]
    dy = target_pos[1] - current_pos[1]
    distance = (dx**2 + dy**2)**0.5
    
    if distance < STOPPING_THRESHOLD:
        return (0, 0)
    
    base_speed = min(MAX_SPEED * dt, distance * (1.0 - TARGET_SMOOTHING))
    decel_factor = 1.0
    
    if distance < DECELERATION_RADIUS:
        decel_factor = max(0.3, (distance / DECELERATION_RADIUS)**0.7)
    
    speed = base_speed * decel_factor
    
    if distance > 0:
        vx = speed * (dx / distance)
        vy = speed * (dy / distance)
    else:
        vx, vy = 0, 0
    
    return (vx, vy)

def main():
    pyautogui.FAILSAFE = False

    model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
    model.conf = MIN_CONFIDENCE

    w, h = pyautogui.size()
    s = 500
    l = (w - s) // 2
    t = (h - s) // 2
    region = (l, t, l + s, t + s)
    
    camera = dxcam.create(output_color="BGR")
    camera.start(region=region, target_fps=60)

    listener = mouse.Listener(on_click=on_click)
    listener.start()

    update_actual_position(*pyautogui.position())
    last_frame_time = time.time()

    while True:
        frame = camera.get_latest_frame()
        if frame is None:
            continue

        results = model(frame, size=640)
        detections = results.xyxy[0].cpu().numpy()
        
        best_conf = MIN_CONFIDENCE
        best_bbox = None
        for *bbox, conf, cls in detections:
            if int(cls) == 0 and conf > best_conf:
                best_conf = conf
                x1, y1, x2, y2 = bbox
                best_bbox = ((x1 + x2) / 2, (y1 + y2) / 2)

        tracker.update_target(best_bbox)

        if should_move and tracker.active:
            current_time = time.time()
            dt = current_time - last_frame_time
            last_frame_time = current_time

            current_pos = pyautogui.position()
            
            if tracker.current_target:
                target_x = l + tracker.current_target[0]
                target_y = t + tracker.current_target[1]
                
                vx, vy = calculate_movement(current_pos, (target_x, target_y), dt)
                
                if abs(vx) > 0 or abs(vy) > 0:
                    dx_move = int(round(vx))
                    dy_move = int(round(vy))
                    
                    send_relative_mouse_move(dx_move, dy_move)
                    update_actual_position(current_pos[0] + dx_move, current_pos[1] + dy_move)

        frame = np.asarray(frame, dtype=np.uint8)
        if tracker.current_target:
            tx = int(tracker.current_target[0])
            ty = int(tracker.current_target[1])
            cv2.circle(frame, (tx, ty), 8, (0, 0, 255), -1)
        
        cv2.imshow("AI Aimbot", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        time.sleep(INPUT_SAMPLE_RATE)

    listener.stop()
    cv2.destroyAllWindows()
    camera.stop()

if __name__ == "__main__":
    main()
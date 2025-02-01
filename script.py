import cv2
import torch
import numpy as np
import dxcam
import time
import ctypes
from pynput import mouse
import win32api
import win32con

aimbot_enabled = False
locked_target = None  
HEAD_OFFSET = -15  # négatif = plus haut, positif = plus bas
SMOOTHNESS = 2   # Plus la valeur est faible plus le mouvement est lent et smooth (réduire si bug de souris)
TARGET_LOCK_THRESHOLD = 20  

user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)
capture_size = 450 
region_left = (screen_width - capture_size) // 2
region_top = (screen_height - capture_size) // 2
region_right = region_left + capture_size
region_bottom = region_top + capture_size
REGION = (region_left, region_top, region_right, region_bottom)

def move_mouse_to_target(target_pos, smoothness=SMOOTHNESS):
    current_pos = win32api.GetCursorPos()  # (x, y)
    dx = target_pos[0] - current_pos[0]
    dy = target_pos[1] - current_pos[1]
    
    move_x = int(dx * smoothness)
    move_y = int(dy * smoothness)
    
    if abs(move_x) < 1 and abs(move_y) < 1:
        return

    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)

def on_click(x, y, button, pressed):
    global aimbot_enabled
    if button == mouse.Button.right:
        aimbot_enabled = pressed
    return True

def start_mouse_listener():
    listener = mouse.Listener(on_click=on_click)
    listener.start()

def detect_targets(model, frame):
    results = model(frame)
    dets = results.xyxy[0].cpu().numpy()
    targets = []
    allowed_classes = [0] 

    for det in dets:
        x1, y1, x2, y2, conf, cls = det
        if conf < model.conf:
            continue
        if int(cls) not in allowed_classes:
            continue
        center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
        targets.append({
            'bbox': (int(x1), int(y1), int(x2), int(y2)),
            'center': center,
            'confidence': conf,
            'class': int(cls)
        })
    return targets

def aimbot_loop(model, camera):
    global locked_target
    prev_time = time.perf_counter()
    while True:
        frame = camera.get_latest_frame()
        if frame is None:
            continue

        now = time.perf_counter()
        fps = 1.0 / (now - prev_time) if (now - prev_time) > 0 else 0
        prev_time = now

        targets = detect_targets(model, frame)
        frame_center = (capture_size // 2, capture_size // 2)

        if locked_target is not None:
            found_target = None
            for target in targets:
                distance = np.hypot(target['center'][0] - locked_target['center'][0],
                                    target['center'][1] - locked_target['center'][1])
                if distance < TARGET_LOCK_THRESHOLD:
                    found_target = target
                    break
            if found_target is not None:
                locked_target = found_target
            else:
                locked_target = None

        if locked_target is None and targets:
            best_detection = None
            best_distance = float('inf')
            for target in targets:
                center = target['center']
                distance = np.hypot(center[0] - frame_center[0], center[1] - frame_center[1])
                if distance < best_distance:
                    best_distance = distance
                    best_detection = target
            locked_target = best_detection

        predicted_target = None
        if locked_target is not None:
            best_center = locked_target['center']
            predicted_target = best_center

        if aimbot_enabled and predicted_target is not None:
            absolute_target = (REGION[0] + predicted_target[0],
                               REGION[1] + predicted_target[1] + HEAD_OFFSET)
            move_mouse_to_target(absolute_target, smoothness=SMOOTHNESS)

        for target in targets:
            x1, y1, x2, y2 = target['bbox']
            conf = target['confidence']
            color = (0, 0, 255) if locked_target is not None and target == locked_target else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{conf:.2f}", (x1, max(y1 - 5, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f"Aimbot: {'ON' if aimbot_enabled else 'OFF'}", (10, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if locked_target is not None:
            cv2.putText(frame, f"Target: {locked_target['center']} Conf: {locked_target['confidence']:.2f}",
                        (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.imshow("Aimbot", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def main():
    start_mouse_listener()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Loading YOLOv5 model (.pt)...")
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    model.to(device)
    model.conf = 0.5
    _ = model(np.zeros((capture_size, capture_size, 3), dtype=np.uint8))
    print("Model loaded.")
    print("Initializing screen capture...")
    camera = dxcam.create(device_idx=0, region=REGION)
    camera.start()
    time.sleep(1)
    
    cv2.namedWindow("Aimbot", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Aimbot", cv2.WND_PROP_TOPMOST, 1)
    
    try:
        aimbot_loop(model, camera)
    except KeyboardInterrupt:
        pass
    finally:
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

import cv2
import torch
import numpy as np
import dxcam
import time
import ctypes
from pynput import mouse
import win32api
import win32con
from config_manager import ConfigManager

config = ConfigManager('config.json')

aimbot_enabled = False
locked_target = None

HEAD_OFFSET = config.get('aimbot.head_offset', -15)
SMOOTHNESS = config.get('aimbot.smoothness', 2)
TARGET_LOCK_THRESHOLD = config.get('aimbot.target_lock_threshold', 20)
CAPTURE_SIZE = config.get('aimbot.capture_size', 450)

user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)
region_left = (screen_width - CAPTURE_SIZE) // 2
region_top = (screen_height - CAPTURE_SIZE) // 2
region_right = region_left + CAPTURE_SIZE
region_bottom = region_top + CAPTURE_SIZE
REGION = (region_left, region_top, region_right, region_bottom)

def move_mouse_to_target(target_pos, smoothness=None):
    if smoothness is None:
        smoothness = config.get('aimbot.smoothness', SMOOTHNESS)
        
    current_pos = win32api.GetCursorPos()
    dx = target_pos[0] - current_pos[0]
    dy = target_pos[1] - current_pos[1]
    
    move_x = int(dx * smoothness)
    move_y = int(dy * smoothness)
    
    if abs(move_x) < 1 and abs(move_y) < 1:
        return

    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)

def on_click(x, y, button, pressed):
    global aimbot_enabled
    activation_button = config.get('controls.activation_button', 'right')
    
    if activation_button == 'right' and button == mouse.Button.right:
        aimbot_enabled = pressed
    elif activation_button == 'left' and button == mouse.Button.left:
        aimbot_enabled = pressed
    return True

def start_mouse_listener():
    listener = mouse.Listener(on_click=on_click)
    listener.start()

def detect_targets(model, frame):
    results = model(frame)
    dets = results.xyxy[0].cpu().numpy()
    targets = []
    allowed_classes = config.get('model.allowed_classes', [0])

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
    
    show_fps = config.get('display.show_fps', True)
    show_target_info = config.get('display.show_target_info', True)
    quit_key = config.get('controls.quit_key', 'q')
    head_offset = config.get('aimbot.head_offset', HEAD_OFFSET)
    target_lock_threshold = config.get('aimbot.target_lock_threshold', TARGET_LOCK_THRESHOLD)
    capture_size = config.get('aimbot.capture_size', CAPTURE_SIZE)
    
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
                if distance < target_lock_threshold:
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
                               REGION[1] + predicted_target[1] + head_offset)
            move_mouse_to_target(absolute_target)

        for target in targets:
            x1, y1, x2, y2 = target['bbox']
            conf = target['confidence']
            color = (0, 0, 255) if locked_target is not None and target == locked_target else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{conf:.2f}", (x1, max(y1 - 5, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        if show_fps:
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        cv2.putText(frame, f"Aimbot: {'ON' if aimbot_enabled else 'OFF'}", (10, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        if show_target_info and locked_target is not None:
            cv2.putText(frame, f"Target: {locked_target['center']} Conf: {locked_target['confidence']:.2f}",
                        (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.imshow(config.get('display.window_name', 'Aimbot'), frame)
        if cv2.waitKey(1) & 0xFF == ord(quit_key):
            break

def main():
    print("AI AIMBOT")
    print(f"Loaded from: {config.config_path}")
    print(f"HEAD_OFFSET: {config.get('aimbot.head_offset')}")
    print(f"SMOOTHNESS: {config.get('aimbot.smoothness')}")
    print(f"CAPTURE_SIZE: {config.get('aimbot.capture_size')}")
    print(f"Confidence threshold: {config.get('model.confidence_threshold')}")
    
    start_mouse_listener()
    
    use_cuda = config.get('performance.use_cuda', True)
    device = torch.device("cuda" if torch.cuda.is_available() and use_cuda else "cpu")
    print(f"Device used: {device}")
    
    print("Loading YOLOv5 model (.pt)...")
    model_name = config.get('model.model_name', 'yolov5s')
    pretrained = config.get('model.pretrained', True)
    model = torch.hub.load('ultralytics/yolov5', model_name, pretrained=pretrained)
    model.to(device)
    model.conf = config.get('model.confidence_threshold', 0.5)
    
    capture_size = config.get('aimbot.capture_size', CAPTURE_SIZE)
    _ = model(np.zeros((capture_size, capture_size, 3), dtype=np.uint8))
    print("Model loaded.")
    
    print("Initializing screen capture...")
    device_idx = config.get('performance.device_idx', 0)
    camera = dxcam.create(device_idx=device_idx, region=REGION)
    camera.start()
    time.sleep(1)
    
    window_name = config.get('display.window_name', 'Aimbot')
    window_topmost = config.get('display.window_topmost', True)
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    if window_topmost:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    
    try:
        aimbot_loop(model, camera)
    except KeyboardInterrupt:
        print("\nStop...")
    finally:
        camera.stop()
        cv2.destroyAllWindows()
        print("Cleaning done")

if __name__ == "__main__":
    main()

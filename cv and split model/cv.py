# moving_camera_passenger_counter_v3.py

import cv2
import numpy as np
from ultralytics import YOLO

# ---------------- CONFIG ----------------

VIDEO_PATH = "videos/Iyyappanthagal .mp4"
MODEL_PATH = "yolov8n.pt"

CONF_THRESHOLD = 0.4
MIN_FRAMES = 10
REL_SPEED_THRESHOLD = 3

TEXTURE_THRESHOLD = 25
EDGE_THRESHOLD = 8

# ---------------- TRACKER ----------------

class Tracker:
    def __init__(self):
        self.next_id = 0
        self.tracks = {}

    def update(self, detections):
        updated_tracks = []

        for det in detections:
            x1, y1, x2, y2, conf = det
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            assigned = False

            for track_id, (tx, ty) in self.tracks.items():
                dist = np.sqrt((cx - tx)**2 + (cy - ty)**2)

                if dist < 50:
                    self.tracks[track_id] = (cx, cy)
                    updated_tracks.append([x1, y1, x2, y2, track_id])
                    assigned = True
                    break

            if not assigned:
                self.tracks[self.next_id] = (cx, cy)
                updated_tracks.append([x1, y1, x2, y2, self.next_id])
                self.next_id += 1

        return updated_tracks

# ---------------- HELPERS ----------------

def get_global_motion(prev_gray, gray):
    flow = cv2.calcOpticalFlowFarneback(
        prev_gray, gray, None,
        0.5, 3, 15, 3, 5, 1.2, 0
    )
    return flow[..., 0].mean(), flow[..., 1].mean()

def relative_speed(positions, gdx, gdy):
    if len(positions) < 2:
        return 0

    dx = positions[-1][0] - positions[-2][0]
    dy = positions[-1][1] - positions[-2][1]

    return np.sqrt((dx - gdx)**2 + (dy - gdy)**2)

def motion_variance(positions):
    if len(positions) < 5:
        return 0

    dxs, dys = [], []
    for i in range(1, len(positions)):
        dxs.append(positions[i][0] - positions[i-1][0])
        dys.append(positions[i][1] - positions[i-1][1])

    return np.var(dxs) + np.var(dys)

def bbox_variation(boxes):
    if len(boxes) < 5:
        return 0

    areas = [(b[2]-b[0])*(b[3]-b[1]) for b in boxes]
    return max(areas) - min(areas)

def is_fake_static(positions):
    if len(positions) < 5:
        return False

    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]

    return (max(xs)-min(xs) < 5) and (max(ys)-min(ys) < 5)

def aspect_ratio(x1, y1, x2, y2):
    return (y2 - y1) / (x2 - x1 + 1e-5)

# 🔥 2D vs 3D filters

def texture_variation(frame, box):
    x1, y1, x2, y2 = box
    crop = frame[y1:y2, x1:x2]

    if crop.size == 0:
        return 0

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    return np.std(gray)

def edge_density(frame, box):
    x1, y1, x2, y2 = box
    crop = frame[y1:y2, x1:x2]

    if crop.size == 0:
        return 0

    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    return np.mean(edges)

# ---------------- INIT ----------------

model = YOLO(MODEL_PATH)
tracker = Tracker()

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("❌ Cannot open video")
    exit()

track_data = {}
counted_ids = set()

prev_gray = None

# ---------------- LOOP ----------------

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if prev_gray is None:
        prev_gray = gray
        continue

    gdx, gdy = get_global_motion(prev_gray, gray)
    prev_gray = gray

    # -------- DETECTION --------
    results = model(frame)[0]
    detections = []

    for box in results.boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])

        if cls == 0 and conf > CONF_THRESHOLD:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append([x1, y1, x2, y2, conf])

    # -------- TRACKING --------
    tracks = tracker.update(detections)

    current_count = 0

    for track in tracks:
        x1, y1, x2, y2, tid = track
        cx, cy = (x1 + x2)//2, (y1 + y2)//2

        if tid not in track_data:
            track_data[tid] = {
                "frames": 0,
                "positions": [],
                "boxes": [],
                "valid": False
            }

        data = track_data[tid]
        data["frames"] += 1
        data["positions"].append((cx, cy))
        data["boxes"].append((x1, y1, x2, y2))

        # -------- FEATURES --------
        rel_speed = relative_speed(data["positions"], gdx, gdy)
        motion_var = motion_variance(data["positions"])
        box_var = bbox_variation(data["boxes"])
        fake_static = is_fake_static(data["positions"])
        ratio = aspect_ratio(x1, y1, x2, y2)

        texture = texture_variation(frame, (x1, y1, x2, y2))
        edges = edge_density(frame, (x1, y1, x2, y2))

        # -------- FINAL FILTER --------
        if (
            data["frames"] >= MIN_FRAMES and
            rel_speed < REL_SPEED_THRESHOLD and
            motion_var > 1 and
            box_var > 500 and
            not fake_static and
            1.2 < ratio < 4.5 and
            texture > TEXTURE_THRESHOLD and
            edges > EDGE_THRESHOLD
        ):
            data["valid"] = True
            counted_ids.add(tid)

        # -------- DRAW --------
        color = (0,255,0) if data["valid"] else (0,0,255)

        if data["valid"]:
            current_count += 1

        cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)
        cv2.putText(frame, f"ID {tid}", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.putText(frame, f"Passengers: {current_count}",
                (40,50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0,255,255), 2)

    cv2.imshow("Passenger Counter V3", frame)

    if cv2.waitKey(30) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

print("Final Passenger Count:", len(counted_ids))
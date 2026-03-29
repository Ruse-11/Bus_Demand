from ultralytics import YOLO
import cv2
import numpy as np

# Load YOLO model once
model = YOLO("yolov8n.pt")

def run_detection(video_path):

    cap = cv2.VideoCapture(video_path)

    frame_skip = 5
    frame_count = 0
    frame_counts = []

    annotated_frame = None

    # Define ROI (adjust manually based on your video)
    # Example: only count people in middle 60% width and upper 80% height
    roi_x_min = 0.2
    roi_x_max = 0.8
    roi_y_min = 0.0
    roi_y_max = 0.85

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue

        h, w, _ = frame.shape

        x_min = int(w * roi_x_min)
        x_max = int(w * roi_x_max)
        y_min = int(h * roi_y_min)
        y_max = int(h * roi_y_max)

        roi_frame = frame[y_min:y_max, x_min:x_max]

        results = model(roi_frame, verbose=False)

        count_in_frame = 0

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]

                if label == "person":
                    count_in_frame += 1

                    # Draw bounding box
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1 = int(x1) + x_min
                    x2 = int(x2) + x_min
                    y1 = int(y1) + y_min
                    y2 = int(y2) + y_min

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

        frame_counts.append(count_in_frame)

        # Save last annotated frame for display
        annotated_frame = frame.copy()

    cap.release()

    if len(frame_counts) == 0:
        avg_count = 0
    else:
        avg_count = int(sum(frame_counts) / len(frame_counts))

    return avg_count, annotated_frame
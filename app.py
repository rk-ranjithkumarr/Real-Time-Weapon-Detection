from __future__ import annotations

import argparse
import csv
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
from ultralytics import YOLO
from huggingface_hub import hf_hub_download
import torch

PROJECT_DIR = Path(__file__).resolve().parent
MODEL_DIR = PROJECT_DIR / "model"
MODEL_PATH = MODEL_DIR / "best.pt"
SNAPSHOT_DIR = PROJECT_DIR / "alerts"
LOG_DIR = PROJECT_DIR / "logs"
LOG_PATH = LOG_DIR / "detections.csv"

MODEL_REPO = "cosgun99/gun-knife-yolo11n"
MODEL_FILE = "best.pt"

# The downloaded model has two classes according to its model card:
# 0 = gun, 1 = knife.
WEAPON_CLASSES = {"gun", "knife"}
DEFAULT_CONFIDENCE = 0.45
DEFAULT_IOU = 0.45
DEFAULT_IMGSZ = 640
MIN_CONSECUTIVE_FRAMES = 1
ALARM_AUDIO_PATH = PROJECT_DIR / "assets" / "weapon_alarm.wav"


def ensure_directories() -> None:
    MODEL_DIR.mkdir(exist_ok=True)
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)


def ensure_model() -> Path:
    ensure_directories()
    if MODEL_PATH.exists() and MODEL_PATH.stat().st_size > 100_000:
        return MODEL_PATH

    print(f"[INFO] Downloading model '{MODEL_REPO}/{MODEL_FILE}' ...")
    print("[INFO] This happens only once and requires an internet connection.")
    downloaded = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILE,
        local_dir=str(MODEL_DIR),
    )
    downloaded_path = Path(downloaded)
    if downloaded_path.resolve() != MODEL_PATH.resolve():
        downloaded_path.replace(MODEL_PATH)
    print(f"[OK] Model ready: {MODEL_PATH}")
    return MODEL_PATH


def log_detection(detected: list[tuple[str, float, tuple[int, int, int, int]]]) -> None:
    ensure_directories()
    new_file = not LOG_PATH.exists()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if new_file:
            writer.writerow(["timestamp", "class", "confidence", "x1", "y1", "x2", "y2"])
        timestamp = datetime.now().isoformat(timespec="seconds")
        for name, confidence, (x1, y1, x2, y2) in detected:
            writer.writerow([timestamp, name, f"{confidence:.4f}", x1, y1, x2, y2])


def start_alarm() -> None:
    """Start a continuous looping siren on Windows until stop_alarm() is called."""
    try:
        import winsound

        if not ALARM_AUDIO_PATH.exists():
            print(f"[WARN] Alarm audio not found: {ALARM_AUDIO_PATH}")
            return

        winsound.PlaySound(
            str(ALARM_AUDIO_PATH),
            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
        )
        print("[ALARM] Continuous alert sound ON")
    except Exception as exc:
        print(f"[WARN] Could not start alarm sound: {exc}")


def stop_alarm() -> None:
    """Stop the continuous alarm sound."""
    try:
        import winsound
        winsound.PlaySound(None, 0)
    except Exception:
        pass

def parse_source(source: str):
    if source.isdigit():
        return int(source)
    return source


def open_capture(source):
    if isinstance(source, int):
        # CAP_DSHOW is usually more reliable on Windows webcams.
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(source)
    else:
        cap = cv2.VideoCapture(source)
    return cap


def draw_status(frame, status: str, weapon_count: int, fps: float) -> None:
    h, w = frame.shape[:2]
    header_height = 70
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, header_height), (25, 25, 25), -1)
    cv2.addWeighted(overlay, 0.80, frame, 0.20, 0, frame)

    status_color = (0, 0, 255) if weapon_count else (0, 190, 0)
    cv2.putText(frame, status, (18, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.75, status_color, 2, cv2.LINE_AA)
    cv2.putText(
        frame,
        f"Weapons: {weapon_count}   FPS: {fps:.1f}   Press Q to quit",
        (18, 56),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )


def run_live(source, confidence: float, iou: float, imgsz: int) -> None:
    model_path = ensure_model()
    print(f"[INFO] Loading YOLO model: {model_path}")
    device = 0 if torch.cuda.is_available() else "cpu"
    device_label = "CUDA GPU" if device == 0 else "CPU"
    print(f"[INFO] Inference device: {device_label}")
    model = YOLO(str(model_path))

    cap = open_capture(source)
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open source {source!r}. For webcam use 0, 1, ...; for video use a valid file path."
        )

    if isinstance(source, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    consecutive_weapon_frames = 0
    alert_active = False
    frame_counter = 0
    fps = 0.0
    fps_timer = time.perf_counter()
    fps_frames = 0

    print("[OK] Real-time detection started.")
    print("[INFO] Press Q in the OpenCV window to stop.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[INFO] End of source or frame could not be read.")
                break

            frame_counter += 1
            fps_frames += 1
            now = time.perf_counter()
            elapsed = now - fps_timer
            if elapsed >= 1.0:
                fps = fps_frames / elapsed
                fps_frames = 0
                fps_timer = now

            results = model.predict(
                source=frame,
                conf=confidence,
                iou=iou,
                imgsz=imgsz,
                verbose=False,
                device=device,
            )
            result = results[0]
            annotated = frame.copy()
            detected: list[tuple[str, float, tuple[int, int, int, int]]] = []

            if result.boxes is not None:
                names = result.names
                for box in result.boxes:
                    cls_id = int(box.cls.item())
                    score = float(box.conf.item())
                    name = str(names[cls_id]).lower()
                    if name not in WEAPON_CLASSES:
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    detected.append((name, score, (x1, y1, x2, y2)))
                    label = f"{name.upper()} {score:.0%}"
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
                    top = max(0, y1 - th - baseline - 8)
                    cv2.rectangle(annotated, (x1, top), (x1 + tw + 10, y1), (0, 0, 255), -1)
                    cv2.putText(
                        annotated,
                        label,
                        (x1 + 5, y1 - 7),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

            if detected:
                consecutive_weapon_frames += 1
            else:
                consecutive_weapon_frames = 0

            weapon_confirmed = consecutive_weapon_frames >= MIN_CONSECUTIVE_FRAMES
            if weapon_confirmed:
                status = "ALERT: WEAPON DETECTED - SIREN ACTIVE"
                if not alert_active:
                    alert_active = True
                    start_alarm()
                    log_detection(detected)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    snapshot_path = SNAPSHOT_DIR / f"weapon_{timestamp}_{frame_counter}.jpg"
                    cv2.imwrite(str(snapshot_path), annotated)
                    print(f"[ALERT] {[(name, round(conf, 3)) for name, conf, _ in detected]}")
                    print(f"[ALERT] Snapshot saved: {snapshot_path}")
            else:
                if alert_active:
                    alert_active = False
                    stop_alarm()
                    print("[ALARM] Continuous alert sound OFF")
                status = "Monitoring - No weapon detected"

            draw_status(annotated, status, len(detected), fps)
            cv2.imshow("Real-Time Weapon Detection", annotated)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
    finally:
        stop_alarm()
        cap.release()
        cv2.destroyAllWindows()
        print("[OK] Detection stopped.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Real-Time Weapon Detection using YOLO11n (gun + knife) with audible alerts."
    )
    parser.add_argument(
        "--source",
        default="0",
        help="Webcam index (0, 1, ...) or video path/URL. Default: 0",
    )
    parser.add_argument("--confidence", type=float, default=DEFAULT_CONFIDENCE, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=DEFAULT_IOU, help="IoU threshold for NMS")
    parser.add_argument("--imgsz", type=int, default=DEFAULT_IMGSZ, help="Inference image size")
    args = parser.parse_args()

    if not 0.05 <= args.confidence <= 0.99:
        parser.error("--confidence must be between 0.05 and 0.99")
    if not 0.05 <= args.iou <= 0.99:
        parser.error("--iou must be between 0.05 and 0.99")

    source = parse_source(args.source)
    try:
        run_live(source, args.confidence, args.iou, args.imgsz)
        return 0
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
        return 0
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        print("[HINT] Run: python app.py --help", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

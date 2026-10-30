# Real-Time Weapon Detection Using Deep Learning

A practical computer-vision project that detects **guns and knives** from a webcam or video using a fine-tuned YOLO11n object-detection model. When a weapon is visible above the confidence threshold, the application:

- draws a red bounding box and confidence score;
- shows an on-screen **WEAPON DETECTED** warning;
- starts a **continuous repeating siren** while a weapon is visible;
- stops the siren automatically as soon as no weapon is detected;
- saves an alert snapshot in `alerts/`;
- appends the event to `logs/detections.csv`.

## Model

The project uses `cosgun99/gun-knife-yolo11n`, a public MIT-licensed YOLO11n model. Its model card defines two classes: `gun` and `knife`, and reports academic test results for those classes. The model author also states that it is intended for academic demonstration rather than standalone safety-critical deployment.

Model page: https://huggingface.co/cosgun99/gun-knife-yolo11n

The model file is downloaded automatically the first time you run the app and stored as `model/best.pt`.

## Windows setup - Python 3.11

### 1. Extract the ZIP

Extract the project to a simple path such as:

`C:\Projects\Real-Time-Weapon-Detection`

Avoid very long nested folder paths.

### 2. Open Command Prompt

Open the project folder, click the address bar in File Explorer, type `cmd`, and press Enter.

### 3. Create the virtual environment

```bat
py -3.11 -m venv .venv
```

### 4. Activate it

```bat
.venv\Scripts\activate
```

You should now see `(.venv)` at the left side of the command line.

### 5. Upgrade pip

```bat
python -m pip install --upgrade pip
```

### 6. Install libraries

```bat
python -m pip install -r requirements.txt
```

Important: this project uses **Ultralytics + PyTorch + OpenCV**, not TensorFlow. On a CPU-only computer, PyTorch will run on the CPU. If you later install a CUDA-enabled PyTorch build for an NVIDIA GPU, the same application can use the GPU automatically.

### 7. Download the trained detector

The first run downloads the model automatically:

```bat
python download_model.py
```

Or skip this command and simply start the camera; `app.py` will download it for you.

### 8. Start real-time webcam detection

```bat
python app.py --source 0
```

A camera window opens. Press **Q** or **Esc** to stop.

You can also double-click:

`run_camera.bat`

## Video file detection

Use:

```bat
python app.py --source "C:\Videos\test.mp4"
```

Or double-click `run_video.bat` and enter the path.

## Useful settings

Lower confidence if detections are being missed:

```bat
python app.py --source 0 --confidence 0.35
```

Use a smaller image size for a slower CPU laptop:

```bat
python app.py --source 0 --imgsz 512
```

Use a larger image size when small objects need better visibility and your hardware is fast enough:

```bat
python app.py --source 0 --imgsz 832
```

## Output folders

After a confirmed detection:

- `alerts/` contains saved detection snapshots.
- `logs/detections.csv` contains timestamp, class, confidence and bounding-box coordinates.
- `model/best.pt` contains the downloaded model.

## Troubleshooting

### Camera is not opening

Try another camera index:

```bat
python app.py --source 1
```

Close Teams, Zoom, OBS or other applications that may already be using the camera.

### `ModuleNotFoundError`

Make sure the virtual environment is active:

```bat
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### TensorFlow installation problems

Do not install TensorFlow for this project. It is not required.

### Model download fails

Check that the computer has internet access and that Hugging Face is reachable. You can also open the model page in a browser:

https://huggingface.co/cosgun99/gun-knife-yolo11n

Download `best.pt` manually and place it here:

`model\best.pt`

Then run:

```bat
python app.py --source 0
```

### Alarm sound

The project includes `assets\weapon_alarm.wav`, a 3-second emergency-style siren. On Windows, Python's built-in `winsound` plays this WAV continuously in a loop while a weapon is detected and stops when the detection clears. No extra audio library is required.

To test the siren independently:

```bat
python test_alarm.py
```

Or double-click `test_alarm.bat`. The test plays the same siren for 10 seconds.

## Project flow

```text
Webcam / Video
      |
      v
OpenCV frame capture
      |
      v
YOLO11n inference
      |
      v
Gun / Knife detections
      |
      +---- confidence threshold
      +---- immediate weapon confirmation
      |
      v
Visual alert + continuous siren
      |
      +---- snapshot
      +---- CSV event log
```

## Safety / limitations

This is an educational computer-vision project. It can produce false positives and false negatives, especially with unusual camera angles, occlusion, poor lighting, toy objects, or images unlike its training data. Do not use the output as the sole basis for emergency, enforcement, or other high-consequence decisions; use appropriate human review.

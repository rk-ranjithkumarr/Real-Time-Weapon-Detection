# Mini Project Report

## Title
Real-Time Weapon Detection Using Deep Learning

## Objective
Detect gun and knife objects from live camera/video frames and immediately trigger a continuous emergency-style siren while a weapon detection is active.

## Deep Learning Method
YOLO11n object detection is used as the inference model. A custom fine-tuned checkpoint is downloaded from the upstream public model repository on first run.

## Core Libraries
- Python 3.11
- Ultralytics
- PyTorch (installed as an Ultralytics dependency)
- OpenCV
- NumPy
- Hugging Face Hub client

## Inputs
- Webcam
- Video file

## Outputs
- Bounding boxes
- Confidence values
- Continuous looping siren while weapon is detected
- Alert snapshots
- CSV event log

## Alert logic
A gun or knife detection above the configured confidence threshold triggers the alert immediately. The included `assets/weapon_alarm.wav` is played in a continuous loop on Windows while the detection remains active. When no weapon is detected, the siren stops automatically. One snapshot and one CSV event are recorded when each new alert episode begins.

## Future improvements
- Add configurable volume and alarm duration settings.
- Add SMS/email notification using an authorized service.
- Add tracking to reduce duplicate alerts.
- Add a custom dataset for the deployment camera domain.
- Add a dashboard for event history.
- Evaluate precision/recall on a held-out local test set before any real deployment.

REAL-TIME WEAPON DETECTION - QUICK START

Windows + Python 3.11

1) Open Command Prompt in this folder.
2) Run:
   install_windows.bat
3) Activate the environment if needed:
   .venv\Scripts\activate
4) Test the siren (optional):
   python test_alarm.py
5) Start webcam detection:
   run_camera.bat

ALERT BEHAVIOR:
- Gun/knife detected -> red box + WARNING + CONTINUOUS LOOPING SIREN.
- Siren remains ON while weapon detection remains active.
- Siren automatically turns OFF when no weapon is detected.
- Detection snapshot -> alerts\
- Detection log -> logs\detections.csv

Press Q or Esc in the camera window to stop.

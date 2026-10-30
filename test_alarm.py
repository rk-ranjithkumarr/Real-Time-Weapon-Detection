"""Play the same continuous siren used by the detector.
Windows only (uses the built-in winsound module).
"""
from pathlib import Path
import time

PROJECT_DIR = Path(__file__).resolve().parent
ALARM = PROJECT_DIR / 'assets' / 'weapon_alarm.wav'

if __name__ == '__main__':
    import winsound
    if not ALARM.exists():
        raise FileNotFoundError(ALARM)
    print('Playing continuous weapon alert for 10 seconds...')
    winsound.PlaySound(str(ALARM), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    try:
        time.sleep(10)
    finally:
        winsound.PlaySound(None, 0)
        print('Alarm stopped.')

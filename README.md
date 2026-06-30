# Gesture-controlled-volume-and-brightness

Control your system volume and screen brightness in real time using just hand gestures — no mouse, no keyboard, just your webcam.

## What it does

- **Volume control** — point with your index finger (thumb out, L-shape) and pinch thumb-to-index closer/farther apart to lower/raise system volume
- **Brightness control** — make a "call me" shape (thumb + pinky extended, other fingers curled) and pinch to adjust screen brightness

## How it works

This project uses [MediaPipe Hands](https://developers.google.com/mediapipe) to detect 21 hand landmarks per frame from a live webcam feed — no custom model training required, it's a pretrained model from Google.

The core logic:
1. **Finger state detection** 
2. **Gesture classification**
3. **Pinch-distance mapping** 
4. **System integration** 

## Tech stack

- Python
- OpenCV — webcam capture and frame processing
- MediaPipe — hand landmark detection
- NumPy — range mapping (interpolation)
- pycaw — Windows audio control
- screen-brightness-control — display brightness control


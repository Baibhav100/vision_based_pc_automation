# Vision-Based PC Automation 🤖✋

This project allows you to control your PC using hand gestures captured by your webcam. It uses **OpenCV**, **MediaPipe**, and **PyAutoGUI**.

## Features
- **Virtual Mouse**: Move your index finger to control the mouse cursor.
- **Screenshot**: Pinch your thumb and index finger together to capture a screenshot.
- **Tab Switching**: Quickly swipe your hand left or right to switch between browser tabs (`Ctrl+Tab` / `Ctrl+Shift+Tab`).

## Setup Instructions

### 1. Prerequisites
Make sure you have Python 3.8+ installed.

### 2. Installation
Install the required libraries:
```bash
pip install -r requirements.txt
```

### 3. Usage
Run the script:
```bash
python automation.py
```

### 4. Controls
- **Cursor**: The mouse follows your index finger tip within the magenta box shown on screen.
- **Screenshot**: Bring your thumb and index finger tips together (pinch).
- **Tab Switch**: Move your hand rapidly horizontally.
- **Exit**: Press 'q' while the camera window is focused.

## Troubleshooting
- **Jittery Mouse**: Ensure good lighting and that your hand is clearly visible. You can adjust the `SMOOTHING` constant in `automation.py`.
- **Latency**: If the video lags, try reducing the camera resolution in the script.
- **Permissions**: On macOS/Linux, you might need to grant Accessibility permissions to your terminal/IDE for PyAutoGUI to control the mouse.

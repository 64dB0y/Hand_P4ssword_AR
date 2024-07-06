### Introduction

This project demonstrates a simple hand tracking and number input system using OpenCV and MediaPipe. The application captures video from the webcam and tracks hand landmarks to allow interaction with a grid of numbers displayed on the screen. Users can enter numbers by pointing to the corresponding cells in the grid, which can be used for password input or other purposes.

### Features

- **Hand Tracking**: Utilizes MediaPipe to detect and track hand landmarks in real-time.
- **Grid Display**: Displays a 4x3 grid with numbers (0-9) and additional 'ENT' and 'DEL' buttons.
- **Interactive Input**: Allows users to input numbers by pointing to the cells in the grid. The 'ENT' button checks if the entered sequence matches a predefined password, and the 'DEL' button deletes the last entered number.

### Requirements

To run this project, you need to install the following Python libraries:
```sh
pip install opencv-python mediapipe
```

### How to Run

To execute the program, run the `maybe_evolve3.py` file:
```sh
python maybe_evolve3.py
```

### Code Overview

The main components of the code include:

- **Drawing Functions**: Functions to draw rectangles and text on the frame.
- **Hand Tracking Functions**: Functions to get fingertip positions and average position of fingertips.
- **Grid Functions**: Functions to draw the grid and determine which cell the hand is pointing to.
- **Main Loop**: Captures video, processes hand landmarks, and updates the grid based on hand position.

Feel free to use and modify this code for your project. If you have any questions or issues, please refer to the documentation or contact the project maintainer.


### Future Plans

Currently, the project only supports a button pressing method for input. In the future, we plan to enhance the repository by adding pattern recognition for input. This will allow for more sophisticated interactions and expand the potential use cases of the system.

Stay tuned for updates as we continue to improve and add new features!
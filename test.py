import cv2
import mediapipe as mp
import numpy as np
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

def draw_grid_with_circles(frame):
    height, width, _ = frame.shape
    square_size = min(height // 4, width // 3)

    for i in range(4):
        for j in range(3):
            start_point = (j * square_size, i * square_size)
            end_point = ((j + 1) * square_size, (i + 1) * square_size)
            color = (255, 255, 255)
            thickness = 1
            frame = cv2.rectangle(frame, start_point, end_point, color, thickness)

            center = (start_point[0] + square_size // 2, start_point[1] + square_size // 2)
            radius = 4
            color = (0, 255, 0)
            thickness = -1
            frame = cv2.circle(frame, center, radius, color, thickness)

    return frame

def check_current_box(x, y, frame):
    height, width, _ = frame.shape
    square_size = min(height // 4, width // 3)

    for i in range(4):
        for j in range(3):
            if (j * square_size <= x < (j + 1) * square_size) and (i * square_size <= y < (i + 1) * square_size):
                box_num = i * 3 + j + 1
                start_point = (j * square_size, i * square_size)
                end_point = ((j + 1) * square_size, (i + 1) * square_size)
                color = (0, 255, 255)
                thickness = 2
                frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
                return box_num, frame

    return None, frame

with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    current_pattern = []
    correct_pattern = ["A", 1, 2, 3, 6, 9, "A"]
    start_time = None
    current_box = None
    entered_start = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        frame.flags.writeable = False
        results = hands.process(frame)

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y = int(index_finger_tip.x * frame.shape[1]), int(index_finger_tip.y * frame.shape[0])

            # Draw 4x3 grid and small circles in the center
            frame = draw_grid_with_circles(frame)

            # Check which box the finger is pointing to and update current_box
            box, frame = check_current_box(x, y, frame)

            if entered_start:
                if current_box != box:
                    current_box = box
                    start_time = time.time()

                # If the finger has been on the circle for more than 2 seconds, change the color to blue
                if current_box and start_time and (time.time() - start_time) > 2:
                    square_size = min(frame.shape[0] // 4, frame.shape[1] // 3)
                    i, j = (current_box - 1) // 3, (current_box - 1) % 3
                    start_point = (j * square_size, i * square_size)
                    end_point = ((j + 1) * square_size, (i + 1) * square_size)
                    color = (255, 0, 0)
                    thickness = 2
                    frame = cv2.rectangle(frame, start_point, end_point, color, thickness)

                    if current_box == 12:  # The special character 'A' is at the bottom right
                        if entered_start:
                            entered_start = False
                            if current_pattern == correct_pattern:
                                print("Pattern is correct!")
                            else:
                                print("Incorrect pattern. Try again.")
                            current_pattern = []
                            start_time = None
                            current_box = None
                        else:
                            entered_start = True
                            current_pattern.append("A")
                    else:
                        current_pattern.append(current_box)

            elif current_box == 12:
                entered_start = True
                current_pattern.append("A")

            cv2.imshow('MediaPipe Hands', frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

cap.release()
cv2.destroyAllWindows()

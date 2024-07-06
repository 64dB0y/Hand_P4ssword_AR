import cv2
import mediapipe as mp
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def get_cell_number(x, y, width, height):
    cell_width = width // 3
    cell_height = height // 3

    cell_x = x // cell_width
    cell_y = y // cell_height

    return cell_y * 3 + cell_x + 1

def draw_grid(frame, cell_number, start_time, ent_button):
    height, width, _ = frame.shape
    cell_width = width // 3
    cell_height = height // 3

    for i in range(1, 3):
        cv2.line(frame, (i * cell_width, 0), (i * cell_width, height), (255, 255, 255), 1)
        cv2.line(frame, (0, i * cell_height), (width, i * cell_height), (255, 255, 255), 1)

    if 1 <= cell_number <= 10:
        x = ((cell_number - 1) % 3) * cell_width
        y = ((cell_number - 1) // 3) * cell_height

        if time.time() - start_time < 2:
            color = (255, 255, 0)
        elif time.time() - start_time < 4:
            if not ent_button:
                color = (0, 0, 255)
            else:
                color = (255, 0, 255)
        else:
            color = (255, 255, 255)

        cv2.rectangle(frame, (x, y), (x + cell_width, y + cell_height), color, 2)

    return frame

correct_pattern = [1, 2, 3, 6, 9, 8, 7, 4, 5]  # 예시 패턴
current_pattern = []
last_added = None
start_time = None

cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        current_cell_number = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                fingertip_x, fingertip_y = int(
                    hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * width), int(
                    hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * height)
                current_cell_number = get_cell_number(fingertip_x, fingertip_y, width, height)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        if current_cell_number:
            if last_added != current_cell_number:
                start_time = time.time()
                last_added = current_cell_number
            elif time.time() - start_time >= 4:
                if current_cell_number not in current_pattern:
                    current_pattern.append(current_cell_number)
                start_time = time.time()

        ent_button = current_cell_number == 10

        frame = draw_grid(frame, current_cell_number, start_time, ent_button)
        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('c'):
            if current_pattern == correct_pattern:
                print("Correct pattern!")
            else:
                print("Incorrect pattern!")
            current_pattern = []

cap.release()
cv2.destroyAllWindows()
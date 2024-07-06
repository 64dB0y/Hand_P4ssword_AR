import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def get_cell_number(x, y, width, height):
    cell_width = width // 3
    cell_height = height // 3

    cell_x = x // cell_width
    cell_y = y // cell_height

    return cell_y * 3 + cell_x + 1

def draw_grid(frame):
    height, width, _ = frame.shape
    cell_width = width // 3
    cell_height = height // 3

    for i in range(1, 3):
        cv2.line(frame, (i * cell_width, 0), (i * cell_width, height), (255, 255, 255), 1)
        cv2.line(frame, (0, i * cell_height), (width, i * cell_height), (255, 255, 255), 1)

correct_pattern = [1, 2, 3, 6, 9, 8, 7, 4, 5]  # 예시 패턴
current_pattern = []

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

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                fingertip_x, fingertip_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * width), int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * height)
                cell_number = get_cell_number(fingertip_x, fingertip_y, width, height)
                if cell_number not in current_pattern:
                    current_pattern.append(cell_number)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        draw_grid(frame)
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
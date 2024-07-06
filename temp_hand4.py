import cv2
import mediapipe as mp
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


def draw_yellow_rectangle(frame, x, y, cell_width, cell_height):
    cv2.rectangle(frame, (x, y), (x + cell_width, y + cell_height), (255, 255, 0), 2)
    return frame


def draw_blue_rectangle(frame, x, y, cell_width, cell_height):
    cv2.rectangle(frame, (x, y), (x + cell_width, y + cell_height), (0, 0, 255), 2)
    return frame


def draw_red_rectangle(frame, x, y, cell_width, cell_height):
    cv2.rectangle(frame, (x, y), (x + cell_width, y + cell_height), (255, 0, 0), 2)
    return frame


def get_cell_number(x, y, width, height):
    cell_width = width // 4
    cell_height = height // 3

    cell_x = x // cell_width
    cell_y = y // cell_height

    return cell_y * 4 + cell_x + 1

def draw_text(frame, x, y, cell_width, cell_height, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_thickness = 2
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_x = x + (cell_width - text_size[0]) // 2
    text_y = y + (cell_height + text_size[1]) // 2
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)
    return frame

def draw_grid(frame, cell_number, start_time, ent_button, cell_width, cell_height):
    height, width, _ = frame.shape
    labels = [str(i) for i in range(1, 10)] + ['0', 'ENT', 'DEL']

    for i in range(1, 4):
        cv2.line(frame, (i * cell_width, 0), (i * cell_width, height), (255, 255, 255), 1)
        cv2.line(frame, (0, i * cell_height), (width, i * cell_height), (255, 255, 255), 1)

    for i, label in enumerate(labels):
        x = (i % 4) * cell_width
        y = (i // 4) * cell_height
        frame = draw_text(frame, x, y, cell_width, cell_height, label)

    if cell_number is not None and 1 <= cell_number <= 12:
        x = ((cell_number - 1) % 4) * cell_width
        y = ((cell_number - 1) // 4) * cell_height

        if start_time is None:
            frame = draw_yellow_rectangle(frame, x, y, cell_width, cell_height)
        elif start_time is not None and time.time() - start_time < 2:
            frame = draw_yellow_rectangle(frame, x, y, cell_width, cell_height)
        elif start_time is not None and time.time() - start_time >= 2 and time.time() - start_time < 4:
            if not ent_button:
                frame = draw_blue_rectangle(frame, x, y, cell_width, cell_height)
            else:
                frame = draw_red_rectangle(frame, x, y, cell_width, cell_height)

    return frame

correct_pattern = [1, 2, 3, 6, 9]  # 예시 패턴
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
        cell_width = width // 4
        cell_height = height // 3
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
            x = ((current_cell_number - 1) % 4) * cell_width
            y = ((current_cell_number - 1) // 4) * cell_height

            if last_added != current_cell_number:
                start_time = time.time()
                last_added = current_cell_number
                frame = draw_yellow_rectangle(frame, x, y, cell_width, cell_height)

            elif time.time() - start_time >= 2 and time.time() - start_time < 4:
                if current_cell_number != 11:
                    frame = draw_blue_rectangle(frame, x, y, cell_width, cell_height)
                else:
                    frame = draw_red_rectangle(frame, x, y, cell_width, cell_height)

                if current_cell_number not in current_pattern and current_cell_number != 11 and current_cell_number != 12:
                    if current_cell_number == 10:  # If the cell is 0, change the number to 0 before appending
                        current_pattern.append(0)
                    else:
                        current_pattern.append(current_cell_number)
                    print("Current pattern:", current_pattern)

            elif time.time() - start_time >= 4:
                start_time = None
                last_added = None
                if current_cell_number in current_pattern:
                    current_pattern.remove(current_cell_number)

            elif time.time() - start_time >= 4:
                start_time = None
                last_added = None
                if current_cell_number in current_pattern:
                    current_pattern.remove(current_cell_number)

        ent_button = current_cell_number == 11
        del_button = current_cell_number == 12

        if del_button and len(current_pattern) > 0:
            current_pattern.pop()
            print("Deleted last item, current pattern:", current_pattern)

        frame = draw_grid(frame, current_cell_number, start_time, ent_button, cell_width, cell_height)
        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif ent_button:
            if current_pattern == correct_pattern:
                print("Correct pattern!")
            else:
                print("Incorrect pattern!")
                current_pattern = []

    cap.release()
    cv2.destroyAllWindows()
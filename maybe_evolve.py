import cv2
import mediapipe as mp
import time
import random

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
input_list = []
labels = [str(i) for i in range(0, 10)] + ['ENT', 'DEL']

def draw_rectangle(frame, x, y, cell_width, cell_height, color):
    cv2.rectangle(frame, (x, y), (x + cell_width, y + cell_height), color, 2)
    return frame

def generate_random_positions(num_cells):
    positions = list(range(num_cells))
    random.shuffle(positions)
    return positions

def draw_text(frame, x, y, cell_width, cell_height, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_thickness = 2
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_x = x + (cell_width - text_size[0]) // 2
    text_y = y + (cell_height + text_size[1]) // 2
    cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)
    return frame

def get_cell_number(x, y, width, height):
    cell_width = width // 4
    cell_height = height // 3

    cell_x = x // cell_width
    cell_y = y // cell_height

    return cell_y * 4 + cell_x + 1

def draw_grid(frame, cell_number, start_time, ent_button, cell_width, cell_height):
    height, width, _ = frame.shape

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
            frame = draw_rectangle(frame, x, y, cell_width, cell_height, (0, 255, 255))
        elif time.time() - start_time < 2:
            frame = draw_rectangle(frame, x, y, cell_width, cell_height, (0, 255, 255))
        elif 2 <= time.time() - start_time < 4:
            frame = draw_rectangle(frame, x, y, cell_width, cell_height, (255, 0, 0))

    return frame

def get_fingertips(hand_landmarks, width, height):
    fingertips = [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                  mp_hands.HandLandmark.RING_FINGER_TIP]
    fingertip_positions = []
    for fingertip in fingertips:
        x, y = int(hand_landmarks.landmark[fingertip].x * width), int(hand_landmarks.landmark[fingertip].y * height)
        fingertip_positions.append((x, y))
    return fingertip_positions

def get_average_position(fingertip_positions):
    avg_x = int(sum([pos[0] for pos in fingertip_positions]) / len(fingertip_positions))
    avg_y = int(sum([pos[1] for pos in fingertip_positions]) / len(fingertip_positions))
    return avg_x, avg_y

cap = cv2.VideoCapture(0)
cell_number = None
start_time = None
last_added = None
ent_button = False
password = [1, 2, 3, 4]

random_positions = generate_random_positions(12)

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
            hand_landmarks = results.multi_hand_landmarks[0]

            # Get the positions of the second, third, and fourth fingertips
            fingertip_positions = get_fingertips(hand_landmarks, width, height)
            # Calculate the average position of the fingertips
            avg_x, avg_y = get_average_position(fingertip_positions)

            if 0 <= avg_x < width and 0 <= avg_y < height:
                current_cell_number = get_cell_number(avg_x, avg_y, width, height)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        frame = draw_grid(frame, current_cell_number, start_time, ent_button, cell_width, cell_height)

        ent_button = current_cell_number == 11
        del_button = current_cell_number == 12

        if start_time is not None and time.time() - start_time >= 2 and last_added != current_cell_number:
            if ent_button:
                if input_list == password:
                    print("Password is correct. Entered numbers:", input_list)
                else:
                    print("Incorrect password. Clearing the input list.")
                    input_list.clear()
            elif del_button:
                if input_list:
                    input_list.pop()
                    print("Deleted last entry. Current input list:", input_list)
            else:
                input_list.append(labels[current_cell_number - 1])
                print("Number", labels[current_cell_number - 1], "pressed")
                print("Current input list:", input_list)
            last_added = current_cell_number

        if current_cell_number:
            x = ((current_cell_number - 1) % 4) * cell_width
            y = ((current_cell_number - 1) // 4) * cell_height

            if last_added != current_cell_number:
                start_time = time.time()
                last_added = current_cell_number
                frame = draw_rectangle(frame, x, y, cell_width, cell_height, (0, 255, 255))

            elif time.time() - start_time >= 1 and time.time() - start_time < 2:
                frame = draw_rectangle(frame, x, y, cell_width, cell_height, (255, 0, 0))

            elif time.time() - start_time >= 2:
                start_time = None
                last_added = None

        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()


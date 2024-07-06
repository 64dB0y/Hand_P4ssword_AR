import cv2
import mediapipe as mp
import time

PINK = (255, 0, 255)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


def draw_grid_with_circles(frame, current_box_num, start_time, box_numbers):
    height, width, _ = frame.shape
    square_size_h = height // 3
    square_size_w = width // 4

    for i in range(3):
        for j in range(4):
            start_point = (j * square_size_w, i * square_size_h)
            end_point = ((j + 1) * square_size_w, (i + 1) * square_size_h)
            color = (255, 255, 255)
            thickness = 1
            frame = cv2.rectangle(frame, start_point, end_point, color, thickness)

            center = (start_point[0] + square_size_w // 2, start_point[1] + square_size_h // 2)
            radius = 6
            color = (0, 255, 0)
            thickness = -1
            frame = cv2.circle(frame, center, radius, color, thickness)

            box_number = box_numbers[i][j]
            box_color = YELLOW if (i, j) == current_box_num and time.time() - start_time < 2 else BLUE if (i,
                                                                                                           j) == current_box_num else (
            255, 255, 255)
            if box_number == "ENT":
                box_color = PINK if (i, j) == current_box_num and time.time() - start_time >= 2 else box_color
            frame = cv2.putText(frame, str(box_number), (center[0] - 10, center[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                box_color, 2, cv2.LINE_AA)

    return frame

def check_current_box(x, y, frame):
    height, width, _ = frame.shape
    square_size_h = height // 3
    square_size_w = width // 4
    i = y // square_size_h
    j = x // square_size_w
    return i, j


def main():
    cap = cv2.VideoCapture(0)
    input_list = []
    current_box_num = None
    start_time = None
    box_numbers = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 0, "ENT", "DEL"]
    ]

    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame.flags.writeable = False
            results = hands.process(frame)
            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    x, y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * frame.shape[1]), int(
                        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * frame.shape[0])
                    new_box_num = check_current_box(x, y, frame)

                    if current_box_num != new_box_num:
                        current_box_num = new_box_num
                        start_time = time.time()
                    else:
                        if time.time() - start_time >= 2:
                            if current_box_num == (2, 2):  # ENT 버튼
                                # 입력 확인
                                print("입력 확인:", input_list)
                                input_list = []
                            elif current_box_num == (2, 3):  # DEL 버튼
                                if input_list:
                                    input_list.pop()
                                    print("삭제 후 리스트:", input_list)
                            else:
                                if len(input_list) < 10:
                                    box_number = box_numbers[current_box_num[0]][current_box_num[1]]
                                    if box_number not in input_list:
                                        input_list.append(box_number)
                                        print("새로운 입력 리스트:", input_list)
                                        current_box_num = None  # 입력 후 상자 인식 해제

            frame = draw_grid_with_circles(frame, current_box_num, start_time, box_numbers)
            cv2.imshow("Frame", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

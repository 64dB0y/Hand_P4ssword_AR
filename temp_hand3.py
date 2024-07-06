import cv2
import mediapipe as mp
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# 노란색 사각형을 그리는 함수
def draw_yellow_rectangle(frame, x, y, cell_width, cell_height):
    cv2.rectangle(frame, (x, y), (x + cell_width, y + cell_height), (255, 255, 0), 2)
    return frame

# 파란색 사각형을 그리는 함수
def draw_blue_rectangle(frame, x, y, cell_width, cell_height):
    cv2.rectangle(frame, (x, y), (x + cell_width, y + cell_height), (0, 0, 255), 2)
    return frame

# 빨간색 사각형을 그리는 함수
def draw_red_rectangle(frame, x, y, cell_width, cell_height):
    cv2.rectangle(frame, (x, y), (x + cell_width, y + cell_height), (255, 0, 255), 2)
    return frame

# 손가락 끝의 위치에 해당하는 셀 번호를 구하는 함수
def get_cell_number(x, y, width, height):
    cell_width = width // 3
    cell_height = height // 3

    cell_x = x // cell_width
    cell_y = y // cell_height

    return cell_y * 3 + cell_x + 1

# 그리드와 사각형을 그리는 함수
def draw_grid(frame, cell_number, start_time, ent_button, cell_width, cell_height):
    height, width, _ = frame.shape

    # 그리드 그리기
    for i in range(1, 3):
        cv2.line(frame, (i * cell_width, 0), (i * cell_width, height), (255, 255, 255), 1)
        cv2.line(frame, (0, i * cell_height), (width, i * cell_height), (255, 255, 255), 1)

    # 사각형 그리기
    if cell_number is not None and 1 <= cell_number <= 10:
        x = ((cell_number - 1) % 3) * cell_width
        y = ((cell_number - 1) // 3) * cell_height

        if start_time is not None and time.time() - start_time < 2:
            frame = draw_yellow_rectangle(frame, x, y, cell_width, cell_height)
        elif start_time is not None and time.time() - start_time >= 2 and time.time() - start_time < 4:
            if not ent_button:
                frame = draw_blue_rectangle(frame, x, y, cell_width, cell_height)
            else:
                frame = draw_red_rectangle(frame, x, y, cell_width, cell_height)
        else:
            color = (255, 255, 255)
            cv2.rectangle(frame, (x, y), (x + cell_width, y + cell_height), color, 2)

    return frame

correct_pattern = [1, 2, 3, 6, 9] # 예시 패턴
current_pattern = []
last_added = None
start_time = None

cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence=0.5,min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

            # 프레임 좌우반전
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape
        cell_width = width // 3
        cell_height = height // 3
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        current_cell_number = None

        # 손이 감지되면 해당 손의 인덱스 손가락 끝 좌표 추출
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                fingertip_x, fingertip_y = int(
                    hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * width), int(
                    hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * height)
                current_cell_number = get_cell_number(fingertip_x, fingertip_y, width, height)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        if current_cell_number:
            x = ((current_cell_number - 1) % 3) * cell_width
            y = ((current_cell_number - 1) // 3) * cell_height

            # 새로운 셀을 선택하면 노란색 사각형을 그리고, 시작 시간을 기록
            if last_added != current_cell_number:
                start_time = time.time()
                last_added = current_cell_number
                frame = draw_yellow_rectangle(frame, x, y, cell_width, cell_height)

            # 2초 이상 지속된 경우 노란색 사각형을 파란색으로 변경 (10번 셀의 경우 빨간색)
            elif time.time() - start_time >= 2 and time.time() - start_time < 4:
                if current_cell_number != 10:
                    frame = draw_yellow_rectangle(frame, x, y, cell_width, cell_height)
                else:
                    frame = draw_red_rectangle(frame, x, y, cell_width, cell_height)

                # 지속 시간이 2초 이상이고 ent_button이 아닌 경우, 현재 셀 번호를 패턴에 추가
                if current_cell_number not in current_pattern and not ent_button:
                    current_pattern.append(current_cell_number)

            # 4초 이상 지속되면 선택 취소
            elif time.time() - start_time >= 4:
                start_time = None
                last_added = None
                current_pattern.remove(current_cell_number)

        # 확인 버튼 확인
        ent_button = current_cell_number == 10

        # 그리드 및 사각형 그리기
        frame = draw_grid(frame, current_cell_number, start_time, ent_button, cell_width, cell_height)
        cv2.imshow("Frame", frame)

        # 키보드 입력 처리
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif ent_button:
            if current_pattern == correct_pattern:
                print("Correct pattern!")
            else:
                print("Incorrect pattern!")

    cap.release()
    cv2.destroyAllWindows()

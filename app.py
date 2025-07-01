import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import pyttsx3
from utilities import *


text_voice = pyttsx3.init()

# define all the mediapipe requirements

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7,max_num_hands = 1)
mp_draw = mp.solutions.drawing_utils


capture = cv2.VideoCapture(0)


pts = deque(maxlen=100)  # max = Last 100 positions of the reference

last_spoken = ""

try:

    while True:
        ret, frame = capture.read()
        frame = cv2.flip(frame, 1)
        if not ret:
            print("failed to capture...")
            break

        h, w, _ = frame.shape
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)

        log = False


        if results.multi_hand_landmarks:    
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    
                x_list = [int(lm.x * w) for lm in hand_landmarks.landmark]
                y_list = [int(lm.y * h) for lm in hand_landmarks.landmark]

                x_min, x_max = min(x_list), max(x_list)
                y_min, y_max = min(y_list), max(y_list)
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)

                bounding_box = [x_min, x_max, y_min, y_max]


                area = (x_max - x_min) * (y_max - y_min)
                depth = hand_landmarks.landmark[0].z 

                if log:
                    loging(area,depth)
                # print("Bounding Box Area:", area, "depth:" , depth)

                centre_x,centre_y = centre_point(bounding_box)

                pts.append((centre_x, centre_y))
                cv2.circle(frame, (centre_x, centre_y), 8, (0, 255, 0), 1)
                
        experiment_mute = False
 
        # Gesture direction
        direction = get_direction(pts)
        if direction and direction != last_spoken:
            print(direction)
            text_voice.say(direction)
            text_voice.runAndWait()

            if direction == "Volume up":
                volume_up()

            elif direction == "Volume down":
                volume_down()

            last_spoken = direction
            pts.clear()

        if experiment_mute:
            if 8400 < area < 8500:
                set_mute_state(True)
                text_voice.say("muted")
                text_voice.runAndWait()
            elif 49000 < area < 50000:
                text_voice.say("un muted")
                text_voice.runAndWait()
                set_mute_state(False)

        pose = get_pose(frame,recognizer)
        if pose == "Closed_Fist":
            set_mute_state(True,text_voice)
        elif pose == "Open_Palm":
            set_mute_state(False,text_voice)

        # Display 
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow("Hand Movement Tracker", frame_bgr)
        if cv2.waitKey(1) & 0xFF == 27:  
            break

    capture.release()
    cv2.destroyAllWindows()

except Exception as e:
    print("exception", e, type(e))
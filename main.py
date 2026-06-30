import cv2
import mediapipe as mp
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc


devices=AudioUtilities.GetSpeakers()
interface=devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume_ctrl=cast(interface, POINTER(IAudioEndpointVolume))
vol_range=volume_ctrl.GetVolumeRange()
MIN_VOL, MAX_VOL=vol_range[0], vol_range[1]

def set_volume(percent):
    percent=max(0, min(100,percent))
    vol_db=np.interp(percent,[0,100], [MIN_VOL, MAX_VOL])
    volume_ctrl.SetMasterVolumeLevel(vol_db, None)

def set_brightness(percent):
    percent = max(0, min(100, percent))
    try:
        sbc.set_brightness(percent)
    except Exception as e:
        pass

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

def get_finger_status(hand_landmarks, handedness_label):
    landmarks=hand_landmarks.landmark
    fingers=[]

    if handedness_label == "Right":
        fingers.append(landmarks[4].x < landmarks[3].x)
    else: 
        fingers.append(landmarks[4].x > landmarks[3].x)

    tips_ids=[8,12,16,20]
    joint_ids=[6,10,14,18]
    for tip, joint in zip(tips_ids, joint_ids):
        if landmarks[tip].y<landmarks[joint].y:
            fingers.append(True)
        else:
            fingers.append(False)   
    
    return fingers

def classify_gesture(fingers):
    if fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
        return "POINT"
    elif all(fingers):
        return "OPEN PALM"
    elif not any(fingers):
        return "FIST"
    elif fingers[0] and not fingers[1] and not fingers[2] and not fingers[3] and fingers[4]:
        return "THUMB_PINKY"
    else:
        return "NONE"    

def get_pinch_distance(hand_landmarks, frame_shape):
    h, w, _=frame_shape
    thumb_tip=hand_landmarks.landmark[4]
    index_tip=hand_landmarks.landmark[8]
    x1,y1= int(thumb_tip.x * w), int(thumb_tip.y * h)
    x2,y2= int(index_tip.x * w), int(index_tip.y * h)
    distance=math.hypot(x2-x1, y2-y1)
    return distance, (x1,y1,x2,y2)




while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
         for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            handedness_label = hand_info.classification[0].label
            fingers=get_finger_status(hand_landmarks, handedness_label)
            gesture=classify_gesture(fingers)



            cv2.putText(frame, f"Gesture: {gesture}", (40,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)


            distance,points=get_pinch_distance(hand_landmarks, frame.shape)
            x1,y1,x2,y2=points
            cv2.line(frame, (x1,y1), (x2,y2),(255,0,255), 3)

            if gesture=='POINT':
                vol_percent=int(np.interp(distance,[ 26,246], [0,100]))
                set_volume(vol_percent)
                cv2.putText(frame, f"Volume:{vol_percent}%", (40,90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

            elif gesture=="THUMB_PINKY":
                bright_percent=int(np.interp(distance, [11,105], [0,100]))
                set_brightness(bright_percent)
                cv2.putText(frame, f"Brightness: {bright_percent}%", (40, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)




    cv2.imshow("Gesture Control", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
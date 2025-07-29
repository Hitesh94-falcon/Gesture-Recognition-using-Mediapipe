from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import os,csv
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

model_path = 'gesture_recognizer.task'
recognizer = vision.GestureRecognizer.create_from_model_path(model_path)



def centre_point(bounding_box):
    centre_x = (bounding_box[0] + bounding_box[1]) // 2
    centre_y = (bounding_box[2] + bounding_box[3]) // 2 
    return centre_x,centre_y

def get_direction(pts):
    if len(pts) >= 30:
        dx = pts[-1][0] - pts[0][0]
        dy = pts[-1][1] - pts[0][1]
        if abs(dx) > 50 and abs(dx) > abs(dy):
            return "Turning Right" if dx > 0 else "Turning Left"
        elif abs(dy) > 50:
            return "Volume down" if dy > 0 else "Volume up"
    return None

def control_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))

volume = control_volume()

def volume_up(step=0.1):
    current = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(min(current + step, 1.0), None)

def volume_down(step=0.1):
    current = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(max(current-step,0.0),None)

def set_mute_state(desired_state,text_voice):
    current = volume.GetMute()
    if desired_state != current:
        volume.SetMute(desired_state, None)
        text_voice.say("Muted" if desired_state else "Unmuted")
        text_voice.runAndWait()

def get_pose(frame, recognizer):
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    result = recognizer.recognize(mp_image)
    if result.gestures:
        return result.gestures[0][0].category_name
    return None

def loging(area,depth):
    csv_path = "logs"
    file_exists = os.path.isfile(os.path.join(csv_path, "logs(1).csv"))
    with open(csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["area", "depth"])
        writer.writerow([area, depth])


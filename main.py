import face_recognition
import cv2
import numpy as np
import json
import requests
from threading import Thread, Lock
from queue import Queue
from utils import *
import time

with open("config.json") as config_file:
    config = json.load(config_file)

ENDPOINT_URL = config["ENDPOINT_URL"]
EVENT_ID = config["EVENT_ID"]
WINDOW_HEIGHT = config["WINDOW_HEIGHT"]
WINDOW_WIDTH = config["WINDOW_WIDTH"]
GUI_OVERLAY_PATH = config["GUI_OVERLAY_PATH"]

GUI_OVERLAY = cv2.imread(GUI_OVERLAY_PATH)
GUI_OVERLAY = cv2.resize(GUI_OVERLAY, (WINDOW_WIDTH, WINDOW_HEIGHT))

video_capture = cv2.VideoCapture(0)
cv2.namedWindow("BLinkIOT", cv2.WINDOW_GUI_NORMAL)
cv2.setWindowProperty("BLinkIOT", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);

face_encoding_dict = {}
event_attendance_dict = {}

known_face_encodings = []
known_face_names = []

face_locations = []
face_encodings = []
face_names = []
is_running = True
last_update_time = None
lock = Lock()

found_users_queue = Queue()

print("event_attendance_dict",event_attendance_dict)

_, frame = video_capture.read() 
detected_users = []
last_detected_time = time.time()

def get_video_capture():
    global frame
    global lock
    global video_capture

    while True: 
        lock.acquire()   
        _, frame = video_capture.read()
        lock.release()

        if not is_running:
            break

def update_detected_users():
    global frame
    global detected_users
    global face_encoding
    global last_detected_time
    global lock

    while True:
        if time.time() - last_detected_time > 1:
            fh, fw, _ = frame.shape
            small_frame = frame
            small_frame = cv2.resize(small_frame, (0, 0), fx=0.25, fy=0.25)

            rgb_small_frame = small_frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

                if (np.amin(face_distances) < 0.4):
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        face_names.append(name)
            
            detected_users = face_names
            last_detected_time = time.time()

        if not is_running:
            break

def get_encodings_attendance():
    global face_encoding_dict
    global event_attendance_dict
    global known_face_encodings
    global known_face_names
    global last_update_time

    face_encoding_dict = load_face_encodings()
    print("face_encoding_dict updated!", face_encoding_dict.keys())
    event_attendance_dict = load_attendance()
    known_face_encodings = []
    known_face_names = []

    for k, v in event_attendance_dict.items():
        username = v["username"]
        if username in face_encoding_dict:
            known_face_encodings.append(face_encoding_dict[username])
            known_face_names.append(username)

    print("event_attendance_dict updated! ", event_attendance_dict)
    last_update_time = time.time()

def update_encodings_attendance():
    while True:
        if time.time() - last_update_time > 10:
            lock.acquire()
            get_encodings_attendance()
            lock.release()
        if not is_running:
            break

def mark_attendance_users():
    while True:
        if not found_users_queue.empty():
            user = found_users_queue.get()
            if event_attendance_dict[user]["attended"] == False:
                print("found user:", user)
                res = requests.post(ENDPOINT_URL+"/markAttendanceForEvent", data={"username": user, "event_id": EVENT_ID})
                if res.status_code == 200 and res.json()["status"] == "SUCCESS":
                    print("Marked attendance for", user)
                    event_attendance_dict[user]["attended"] = True
                else:
                    print("ERROR while marking attendance: ", res.json())
        if not is_running:
            break

get_encodings_attendance()

mark_attendance_thread = Thread(target=mark_attendance_users)
mark_attendance_thread.start()
update_encodings_attendance_thread = Thread(target=update_encodings_attendance)
update_encodings_attendance_thread.start()

get_video_capture_thread = Thread(target=get_video_capture)
get_video_capture_thread.start()
update_detected_users_thread = Thread(target=update_detected_users)
update_detected_users_thread.start()

while True:
    display_frame = frame
    display_frame = cv2.resize(display_frame, (0, 0), fx=1.5, fy=1.5)
    fh, fw, _ = display_frame.shape
            
    for name in detected_users:
        if name in event_attendance_dict \
        and event_attendance_dict[name]["registered"] == True \
        and  event_attendance_dict[name]["attended"] == False:
            cv2.rectangle(display_frame, (0, fh-100), (fw, fh), (209, 136,2), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            displayname = event_attendance_dict[name]["displayname"]
            cv2.putText(display_frame, "Hello " + displayname + "!", (10, fh-60), font, 1.2, (255, 255, 255), 2)
            cv2.putText(display_frame, "We're checking you in...", (10, fh-20), font, 1.0, (255, 255, 255), 1)
            found_users_queue.put(name)
            break

        elif name in event_attendance_dict \
        and event_attendance_dict[name]["registered"] == True \
        and event_attendance_dict[name]["attended"] == True:
            cv2.rectangle(display_frame, (0, fh-100), (fw, fh), (60, 142, 56), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            displayname = event_attendance_dict[name]["displayname"]
            cv2.putText(display_frame, "Welcome " + displayname + "!", (10, fh-60), font, 1.2, (255, 255, 255), 2)
            cv2.putText(display_frame, "You're checked in.", (10, fh-20), font, 1.0, (255, 255, 255), 1)
            break

        elif name in event_attendance_dict \
        and event_attendance_dict[name]["registered"] == False:
            cv2.rectangle(display_frame, (0, fh-100), (fw, fh), (28,28,183), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            displayname = event_attendance_dict[name]["displayname"]
            cv2.putText(display_frame, "Hello " + displayname + "!", (10, fh-60), font, 1.2, (255, 255, 255), 2)
            cv2.putText(display_frame, "It seems like you're not registered", (10, fh-20), font, 1.0, (255, 255, 255), 1)
            break
    
    
    display_gui = GUI_OVERLAY
    
    x_margin = int((WINDOW_WIDTH - fw) / 2) 
    y_margin = int((WINDOW_HEIGHT - fh) / 2)

    display_gui[75: 75 + fh ,x_margin: -x_margin,:] = display_frame

    cv2.imshow('BLinkIOT', display_gui)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        is_running = False
        break

save_attendance(event_attendance_dict)
video_capture.release()
cv2.destroyAllWindows()
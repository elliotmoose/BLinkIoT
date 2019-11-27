import face_recognition
import cv2
import numpy as np
import json
import requests
from threading import Thread
from queue import Queue
from utils import *

with open("config.json") as config_file:
    config = json.load(config_file)

ENDPOINT_URL = config["ENDPOINT_URL"]
EVENT_ID = config["EVENT_ID"]

video_capture = cv2.VideoCapture(-1)

face_encoding_dict = load_face_encodings()
event_attendance_dict = load_attendance()

known_face_encodings = []
known_face_names = []

for k, v in event_attendance_dict.items():
    username = v["username"]
    known_face_encodings.append(face_encoding_dict[username])
    known_face_names.append(username)

face_locations = []
face_encodings = []
face_names = []
is_running = True

found_users_queue = Queue()

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

mark_attendance_thread = Thread(target=mark_attendance_users)
mark_attendance_thread.start()

process_this_frame = True
while True:
    ret, frame = video_capture.read()
    fh, fw, _ = frame.shape
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    rgb_small_frame = small_frame[:, :, ::-1]

    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            face_names.append(name)

    process_this_frame = not process_this_frame

    for name in face_names:
        if name in event_attendance_dict and event_attendance_dict[name]["attended"] == False:
            cv2.rectangle(frame, (0, fh-100), (fw, fh), (209, 136,2), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            displayname = event_attendance_dict[name]["displayname"]
            cv2.putText(frame, "Hello " + displayname + "!", (10, fh-60), font, 1.2, (255, 255, 255), 2)
            cv2.putText(frame, "We're checking you in...", (10, fh-20), font, 1.0, (255, 255, 255), 1)
            found_users_queue.put(name)
            break
        elif name in event_attendance_dict and event_attendance_dict[name]["attended"] == True:
            cv2.rectangle(frame, (0, fh-100), (fw, fh), (60, 142, 56), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            displayname = event_attendance_dict[name]["displayname"]
            cv2.putText(frame, "Welcome " + displayname + "!", (10, fh-60), font, 1.2, (255, 255, 255), 2)
            cv2.putText(frame, "You're checked in.", (10, fh-20), font, 1.0, (255, 255, 255), 1)
            break
        
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        is_running = False
        break

save_attendance(event_attendance_dict)
video_capture.release()
cv2.destroyAllWindows()
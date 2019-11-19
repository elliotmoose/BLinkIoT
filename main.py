import face_recognition
import cv2
import time
from utils import *

# TODO: possibly speed up video fps

face_encoding_dict = load_face_encodings()
event_attendance_dict = load_attendance()

video_capture = cv2.VideoCapture(-1)

checkin_frame = None
checkin_user = None

while True:
    ret, frame = video_capture.read()
    h, w, _ = frame.shape

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    found_face_locations = face_recognition.face_locations(small_frame)
    found_face_encodings = face_recognition.face_encodings(small_frame, found_face_locations)

    found_users = []

    for face_encoding in found_face_encodings:
        found_user = match_encodings(face_encoding_dict, face_encoding, 0.8)
            
        if (found_user):
            found_users.append(found_user)
    
    for user in found_users:
        username = user["username"]
        if username in event_attendance_dict and event_attendance_dict[username]["checked_in"] == False:
            checkin_frame = frame

            cv2.rectangle(checkin_frame, (0,h - 100), (w,h), (31, 69, 30), -1)
            font = cv2.FONT_HERSHEY_DUPLEX
            welcome_text = "Welcome " + user["first_name"] + "!"
            cv2.putText(checkin_frame, welcome_text, (10, h-60), font, 1.5, (255,255,255), 2)
            cv2.putText(checkin_frame, "We're checking you in ...", (10, h-20), font, 1.0, (255,255,255), 1)

            checkin_user = username
            event_attendance_dict[username]["checked_in"] = True
            print(username, "has been checked in")
            break

    
    if type(checkin_frame) != type(None):
        cv2.imshow('Video', checkin_frame)
        check_in(checkin_user)
        checkin_user = None
        checkin_frame = None
    else:
        cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


#save_attendance(event_attendance_dict)
video_capture.release()
cv2.destroyAllWindows()
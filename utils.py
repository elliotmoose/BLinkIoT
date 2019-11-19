import json
import face_recognition
import numpy as np
import math
import time


def load_face_encodings():
    # TODO: load face encoding information from server
    with open('face_encodings.json', 'r') as f:
        face_encoding_dict = json.load(f)

    return face_encoding_dict


def load_attendance():
    # TODO: load attendance information from server
    with open('event_attendance.json', 'r') as f:
        event_attendance_dict = json.load(f)

    return event_attendance_dict


def save_attendance(event_attendance_dict):
    with open('event_attendance.json', 'w') as f:
        json.dump(event_attendance_dict, f)


def check_in(user):
    # TODO: implement sending check-in to server
    time.sleep(2)


def match_encodings(encoding_dict, input_encoding, threshold_distance=0.5):
    """
    encoding dict: dictionary of face encodings
    input_encoding : an np array
    threshold_distance: float, default 0.5
    """

    min_distance = math.inf
    matched_user = None

    for _, user in encoding_dict.items():

        face_distance = face_recognition.face_distance([user["face_encoding"]],input_encoding)[0]
        
        if face_distance < threshold_distance and face_distance < min_distance:
            min_distance = face_distance
            matched_user = user
            
    return matched_user
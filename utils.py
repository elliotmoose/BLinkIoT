import json
import face_recognition
import numpy as np
import math
import time
import requests

with open("config.json") as config_file:
    config = json.load(config_file)

OFFLINE_MODE = config["OFFLINE_MODE"]
DEBUG = config["DEBUG"]

def load_face_encodings():
    # TODO: load face encoding information from server
    if not OFFLINE_MODE:
        pass
    with open('face_encodings.json', 'r') as f:
        face_encoding_dict = json.load(f)

    return face_encoding_dict


def load_attendance():
    # TODO: load attendance information from server
    if not OFFLINE_MODE:
        pass
    with open('event_attendance.json', 'r') as f:
        event_attendance_dict = json.load(f)

    return event_attendance_dict


def save_attendance(event_attendance_dict):
    if DEBUG:
        return
    with open('event_attendance.json', 'w') as f:
        json.dump(event_attendance_dict, f)
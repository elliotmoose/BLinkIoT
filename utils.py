import json
import face_recognition
import numpy as np
import math
import time
import requests

with open("config.json") as config_file:
    config = json.load(config_file)

ENDPOINT_URL = config["ENDPOINT_URL"]
EVENT_ID = config["EVENT_ID"]
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
        res = requests.post(url=ENDPOINT_URL+"/registrationsForEvent", data={"event_id" : EVENT_ID})
        if res.status_code == 200 and res.json()["status"] == "SUCCESS":
            event_attendance_dict = {}
            for user in res.json()["data"]:
                username = user["username"]
                attended = user["attended"]
                event_attendance_dict[username] = {"username": username, "attended": attended}
        else:
            print("ERROR!", res.json())
            print("Loading from locally saved event_attendance.json...")
            with open('event_attendance.json', 'r') as f:
                event_attendance_dict = json.load(f)

    else:
        with open('event_attendance.json', 'r') as f:
            event_attendance_dict = json.load(f)

    return event_attendance_dict


def save_attendance(event_attendance_dict):
    if DEBUG:
        return
    else:
        with open('event_attendance.json', 'w') as f:
            json.dump(event_attendance_dict, f)
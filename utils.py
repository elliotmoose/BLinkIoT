import json
import face_recognition
import numpy as np
import math
import time
import requests
from queue import Queue
from concurrent.futures import ThreadPoolExecutor


with open("config.json") as config_file:
    config = json.load(config_file)

ENDPOINT_URL = config["ENDPOINT_URL"]
EVENT_ID = config["EVENT_ID"]
OFFLINE_MODE = config["OFFLINE_MODE"]
DEBUG = config["DEBUG"]

def load_face_encodings():
    if not OFFLINE_MODE:
        res = requests.get(url=ENDPOINT_URL+"/getFaceEncodings")
        if res.status_code == 200:
            face_encoding_dict = res.json()
        else:
            print("ERROR loading face econdings from server! \nLoading from locally saved face_encodings.json...")
            with open('face_encodings.json', 'r') as f:
                face_encoding_dict = json.load(f)
    else:
        with open('face_encodings.json', 'r') as f:
            face_encoding_dict = json.load(f)

    return face_encoding_dict


def get_displayname(username,queue):
    res = requests.post(url=ENDPOINT_URL+"/getUser", data={"username":username})
    if res.status_code == 200 and res.json()["status"] == "SUCCESS":
        queue.put((username,res.json()["data"]["displayname"])) 
    else:
        queue.put((username,"")) 

def load_attendance():
    if not OFFLINE_MODE:
        res = requests.post(url=ENDPOINT_URL+"/registrationsForEvent", data={"event_id" : EVENT_ID})
        if res.status_code == 200 and res.json()["status"] == "SUCCESS":
            event_attendance_dict = {}
            for user in res.json()["data"]:
                username = user["username"]
                attended = user["attended"]
                event_attendance_dict[username] = {"username": username, "attended": attended}

            usernames = [k for k in event_attendance_dict]
            username_queue = Queue()
            with ThreadPoolExecutor(max_workers=5) as executor:
                for username in usernames:
                    executor.submit(get_displayname, username, username_queue)

            while username_queue.qsize() != 0:
                username, displayname  = username_queue.get_nowait()
                event_attendance_dict[username]["displayname"] = displayname

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
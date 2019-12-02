import cv2
from threading import Thread, Lock


video_capture = cv2.VideoCapture(-1)

_ , frame = video_capture.read()

lock = Lock()

def get_video_capture():
    global frame
    global video_capture

    while True: 
        lock.acquire()
        _ , frame = video_capture.read()
        lock.release()

t1 = Thread(target=get_video_capture)
t1.start()

while True:
    cv2.imshow("Video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break
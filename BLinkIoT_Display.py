import cv2
import numpy as np

class BLinkIoT_Display:
    def __init__(self):
        '''
        frame : a cv2 image
        '''
        self.frame = 128 * np.zeros(shape=[512, 512, 3], dtype=np.uint8)


    def update_frame(self, frame):
        self.frame = frame


    def update_display(self):
        cv2.imshow('BLinkIoT Display', self.frame)
        cv2.waitKey(25)


    def add_identified_face(self, displayed_name, top, right, bottom, left):
        cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(self.frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(self.frame, displayed_name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


    def add_unidentified_face(self, top, right, bottom, left):

        cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(self.frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(self.frame, "unknown", (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
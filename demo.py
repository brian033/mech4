import numpy as np
import cv2
import serial
# import cup

# ser = serial.Serial('', 9600)


def getContours(imgcontours, state):
    grey = cv2.cvtColor(imgcontours, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey, (5, 5), 0)
    edge = cv2.Canny(blur, 100, 255)
    kernel = np.ones((4, 4))
    dilate = cv2.dilate(edge, kernel, 1)
    opening = cv2.morphologyEx(dilate, cv2.MORPH_OPEN, kernel)
    contours, hierarchy = cv2.findContours(
        opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for i in contours:
        area = cv2.contourArea(i)
        if area > 1500:
            arclen = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, arclen*0.02, True)
    return 0


while True:
    cap = cv2.VideoCapture(-1)

    # cup.cupdetect()

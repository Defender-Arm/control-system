# https://docs.opencv.org/3.4/da/d97/tutorial_threshold_inRange.html

from __future__ import print_function
import cv2 as cv
import argparse
import numpy as np
max_value = 255
max_value_H = 360//2
low_H = 170
low_S = 120
low_V = 100
high_H = 10
high_S = max_value
high_V = max_value
window_capture_name = 'Video Capture'
window_detection_name = 'Object Detection'
low_H_name = 'Low H'
low_S_name = 'Low S'
low_V_name = 'Low V'
high_H_name = 'High H'
high_S_name = 'High S'
high_V_name = 'High V'
def on_low_H_thresh_trackbar(val):
    global low_H
    global high_H
    low_H = val
    #low_H = min(high_H-1, low_H)
    cv.setTrackbarPos(low_H_name, window_detection_name, low_H)
def on_high_H_thresh_trackbar(val):
    global low_H
    global high_H
    high_H = val
    #high_H = max(high_H, low_H+1)
    cv.setTrackbarPos(high_H_name, window_detection_name, high_H)
def on_low_S_thresh_trackbar(val):
    global low_S
    global high_S
    low_S = val
    low_S = min(high_S-1, low_S)
    cv.setTrackbarPos(low_S_name, window_detection_name, low_S)
def on_high_S_thresh_trackbar(val):
    global low_S
    global high_S
    high_S = val
    high_S = max(high_S, low_S+1)
    cv.setTrackbarPos(high_S_name, window_detection_name, high_S)
def on_low_V_thresh_trackbar(val):
    global low_V
    global high_V
    low_V = val
    low_V = min(high_V-1, low_V)
    cv.setTrackbarPos(low_V_name, window_detection_name, low_V)
def on_high_V_thresh_trackbar(val):
    global low_V
    global high_V
    high_V = val
    high_V = max(high_V, low_V+1)
    cv.setTrackbarPos(high_V_name, window_detection_name, high_V)
parser = argparse.ArgumentParser(description='Code for Thresholding Operations using inRange tutorial.')
parser.add_argument('--camera', help='Camera divide number.', default=1, type=int)
args = parser.parse_args()
cap1 = cv.VideoCapture(1, cv.CAP_DSHOW)
cap1.set(cv.CAP_PROP_FRAME_WIDTH, 20)
cap1.set(cv.CAP_PROP_FRAME_HEIGHT, 20)
cap2 = cv.VideoCapture(2, cv.CAP_DSHOW)
cap2.set(cv.CAP_PROP_FRAME_WIDTH, 20)
cap2.set(cv.CAP_PROP_FRAME_HEIGHT, 20)
cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)
cv.createTrackbar(low_H_name, window_detection_name , low_H, max_value_H, on_low_H_thresh_trackbar)
cv.createTrackbar(high_H_name, window_detection_name , high_H, max_value_H, on_high_H_thresh_trackbar)
cv.createTrackbar(low_S_name, window_detection_name , low_S, max_value, on_low_S_thresh_trackbar)
cv.createTrackbar(high_S_name, window_detection_name , high_S, max_value, on_high_S_thresh_trackbar)
cv.createTrackbar(low_V_name, window_detection_name , low_V, max_value, on_low_V_thresh_trackbar)
cv.createTrackbar(high_V_name, window_detection_name , high_V, max_value, on_high_V_thresh_trackbar)
cv.resizeWindow(window_detection_name, 1600, 1200)


def process_frame(frame):
    frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    frame_threshold_1 = cv.inRange(frame_HSV, (low_H, low_S, low_V), (180, high_S, high_V))
    frame_threshold_2 = cv.inRange(frame_HSV, (0, low_S, low_V), (high_H, high_S, high_V))
    frame_threshold = frame_threshold_1 + frame_threshold_2

    kernel = np.ones((5, 5), np.uint8)
    frame_threshold = cv.morphologyEx(frame_threshold, cv.MORPH_CLOSE, kernel)
    contours, _ = cv.findContours(frame_threshold, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv.contourArea)
        rect = cv.minAreaRect(largest_contour)
        box = cv.boxPoints(rect).astype(int)
        center = (int(rect[0][0]), int(rect[0][1]))
        cv.drawContours(frame, [box], 0, (0, 255, 0), 2)
        cv.circle(frame, center, 5, (255, 0, 0), -1)
    return frame, frame_threshold


while True:
    ret, frame1 = cap1.read()
    if frame1 is None:
        break
    ret, frame2 = cap2.read()
    if frame2 is None:
        break
    frame1, mask1 = process_frame(frame1)
    frame2, mask2 = process_frame(frame2)




    cv.imshow(window_capture_name, np.hstack((frame1, frame2)))
    cv.imshow(window_detection_name, np.hstack((mask1, mask2)))

    key = cv.waitKey(30)
    if key == ord('q') or key == 27:
        break
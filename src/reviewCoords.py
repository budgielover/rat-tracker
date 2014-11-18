#!/usr/bin/env python

# builtin
from itertools import islice, izip
from math import sqrt
import sys
import random
import csv

# 3rd party
import cv2
import cv2.cv
import numpy
from numpy import unravel_index

def writeCSV(data, file):
    with open(file, 'wb') as csvfile:
        coordwriter = csv.writer(csvfile)
        for x, y in data:
            coordwriter.writerow([x, y])

def reviewCoords(data, f):
    """
    This simply plays the video back frame by frame superimposing the points from the
    rest of the function onto it. It allows the user to click to change the point if it
    seems to be deviating too far.
    """
    global corrected

    def on_mouse(event, x, y, flag, param):
        if(event==cv2.EVENT_LBUTTONDOWN):
            global newPoint, corrected
            newPoint = (x, y)
            corrected = True
            redraw()

    def redraw():
        drawFrame = frame.copy()
        if point != ([], []):
            cv2.circle(drawFrame, point, 4, (0, 0, 255))
        cv2.circle(drawFrame, newPoint, 4, (0, 255, 0))
        cv2.imshow("frame", drawFrame)
    def nothing(x):
        pass

    cv2.namedWindow('frame')
    cv2.setMouseCallback('frame', on_mouse)

    length=len(data)
    cap = cv2.VideoCapture(f)

    switch = '1 : OFF+Enter \n0 : ON'
    cv2.createTrackbar(switch, 'frame',0,1,nothing)
    num = 'frame number'
    cv2.createTrackbar(num, 'frame',1,length,nothing)

    n=0
    preframe=1
    while n<length:
        corrected = False
        n=n+1
        point=data[n-1]
        cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,n-1)
        ret, frame = cap.read()
        if point != ([], []):
            cv2.circle(frame, point, 4, (0, 0, 255))
        cv2.imshow("frame", frame)
        cv2.waitKey()
        if(corrected):
            print("rewrote frame {}".format(n))
            data[n-1] = newPoint
        s = cv2.getTrackbarPos(switch,'frame')
        framenum = cv2.getTrackbarPos(num,'frame')        
        if s == 1:
            break
        if framenum!=preframe:
            n=framenum-1
            preframe=framenum       
    cap.release()
    

    
    
def run():
    total = len(sys.argv)
    cmdargs = str(sys.argv)
    print ("The total numbers of args passed to the script: %d " % total)
    print ("Args list: %s " % cmdargs)
    # Pharsing args one by one 
    with open(str(sys.argv[1])) as csvfile:
        data = [(int(x), int(y)) for x, y in csv.reader(csvfile, delimiter= ',')]
    print data
    reviewCoords(data, str(sys.argv[2]))
    writeCSV(data, str(sys.argv[1]))
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    run()
        

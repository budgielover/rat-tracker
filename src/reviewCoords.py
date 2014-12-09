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
	"""
	Writes coordinates from data list into CSV file
	"""
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
    def help(image):
        image1=image.copy()
        image2=image.copy()
        image3=image.copy()
        cv2.putText(image, "press any key to the next frame", (10,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
        cv2.imshow("frame", image)
        k=cv2.waitKey()
        cv2.putText(image1, "or drag trackbar to a certain frame", (10,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
        cv2.imshow("frame", image1)
        k=cv2.waitKey()
        cv2.putText(image2, "revisement will be recorded when exiting", (10,100), cv2.FONT_HERSHEY_SIMPLEX, 0.45, 255)
        cv2.imshow("frame", image2)
        k=cv2.waitKey()
        cv2.putText(image3, "ok let's start :)", (10,100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
        cv2.imshow("frame", image3)
        k=cv2.waitKey()

    cv2.namedWindow('frame')
    cv2.setMouseCallback('frame', on_mouse)
    length=len(data)
    cap = cv2.VideoCapture(f)

    num = 'Framenum'
    cv2.createTrackbar(num, 'frame',1,length,nothing)

    n=0
    preframe=1
    while n<length:
        corrected = False
        n=n+1
        point=data[n-1]
        cv2.setTrackbarPos(num, 'frame', n)
        cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,n-1)
        ret, frame = cap.read()
        if point != ([], []):
            cv2.circle(frame, point, 4, (0, 0, 255))
        cv2.putText(frame, "Help:h Exit:ESC", (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 255)
        cv2.imshow("frame", frame)
        k=cv2.waitKey()
        if k == 27:         # wait for ESC key to exit
            break
        if k == 104:
            help(frame)
        if(corrected):
            print("rewrote frame {}".format(n))
            data[n-1] = newPoint
        framenum = cv2.getTrackbarPos(num,'frame')        
        if framenum!=preframe:
            n=framenum-1
            preframe=framenum       
    cap.release()
    

    
    
def run():
	"""
	Runs the routine to superimpose points and 
	allow user to correct data and then save 
	"""
    total = len(sys.argv)
    cmdargs = str(sys.argv)
    # Pharsing args one by one 
    with open(str(sys.argv[1])) as csvfile:
        data = [(int(x), int(y)) for x, y in csv.reader(csvfile, delimiter= ',')]
    reviewCoords(data, str(sys.argv[2]))
    writeCSV(data, str(sys.argv[1]))
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    run()


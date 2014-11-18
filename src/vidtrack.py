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
from PyQt4 import QtGui, QtCore
# Settings
N = 1
MAX_SEP = 10

EXPECTED_SEP = 7
EXPECTED_MOVEMENT = 5
MAX_EXPECTED_MOVEMENT = 20
SAT_THRESHOLD = 8

JUMP = 600
SAME = 10
DIST = 100

###############################################################################

def frames(videoFile):
    """
    Generator for frames from a video file.
    Yields (frameNum, totalFrames, frame) tuples.
    FrameNum starts from 1.
    """
    cap = cv2.VideoCapture(videoFile)
    total = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    n = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        n += 1
        yield (n, total, frame)	
    cap.release()

def brightest(frame, n, bgmask = None):
    """
    Returns the locations of the brightest n spots in the frame
    This isn't quite working right and I'm not sure why...
    """
    frame = frame.copy()
    for _ in range(0, n):

        #Haoyu's revise
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(frame, None)
        #previous version: minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(frame, bgmask)

        #print frame  
        yield maxLoc
        frame[maxLoc[1], maxLoc[0]] = 0 # so it won't be found next

def mostColorful(channels, n, channel, bgmask=None):
    """
    Channels should be output of cv2.split(img).
    Returns the locations of the n most pure examples of the specified channel.
    Values for channel number depend on your image format, but usually:
        0 = blue
        1 = green
        2 = red
    """
    primary = channels[channel]
    others = channels[:channel] + channels[channel+1:]
    for other in others:
        primary = cv2.addWeighted(primary, 1, other, -0.5, 0)
    return brightest(primary, n, bgmask)

def interpolate(x, y, alpha):
    return x * (1 - alpha) + y * alpha

def simpleComponents(img):
    """
    input: b/w image
    output: generator of (pos, area) tuples
    """
    blobs, _ = cv2.findContours(img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for blob in blobs:
        area = cv2.contourArea(blob)
        center, radius = cv2.minEnclosingCircle(blob)
        if area > 0:
            yield (center, area)

def dist(pt1, pt2):
    dx = pt1[0] - pt2[0]
    dy = pt1[1] - pt2[1]
    return sqrt(dx**2 + dy**2)

def minDist(pt, pts):
    return min(dist(pt, p) for p in pts)

def countChannel(img, pt, radius, channel):
    count = 0
    for x in range(pt[0] - radius, pt[0] + radius + 1):
        for y in range(pt[1] - radius, pt[1] + radius + 1):
            d = dist((x, y), pt)
            if d <= radius and x > 0 and y > 0 and x < img.shape[0] and y < img.shape[1]:
                count += img[x,y][channel]
    return count

def findBackground(f, alpha):

    """
    A basic wrapper for an OpenCV function that creates a static averaged image as the 'background'
    which will be subtracted out of subsequent frames
    """

    for n, total, frame in frames(f):
        if n == 1:
            avg = numpy.float32(frame)
        else:
            cv2.accumulateWeighted(frame, avg, alpha)

    bg = cv2.convertScaleAbs(avg)
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)

    return bg

def candidatePoints(f):
    """
    For an image file, yields (redPoints, greenPoints) for each frame
    """

    # First, find background composite of the whole video
    bg = findBackground(f, 0.01)
    print("Finished averaging background frame")
    for n, total, frame in frames(f):
        frame = frame.copy()
        if n % 1000 == 0:
            print("Processed {} of {}".format(n, total))
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #work with the frame in the hsv color color space to better detect red and green
        hue, sat, _ = cv2.split(hsv)
        #using the lab color space for a better representation of luminescence and brightness
        lum, _, _ = cv2.split(lab)

        #subtract out the background from the lum color space to find the brightest pixels
        BGsubtract = cv2.subtract(lum, bg)
        minVal, maxVal, _, _ = cv2.minMaxLoc(BGsubtract)
        #creates a threshold of the brightest 30% of points
        threshold = interpolate(minVal, maxVal, 0.3)
        _, fgmask = cv2.threshold(BGsubtract, threshold, 255, cv2.THRESH_BINARY)

        # a saturation threshold to detect the "most colorful" pixels
        smask = cv2.inRange(sat, SAT_THRESHOLD, 255)

        # using the saturation mask as well as the forground and brightness maps find the most likely
        # points for red and greens
        green = cv2.inRange(hue, 80, 100)
        gmask = cv2.bitwise_and(green, fgmask)
        gsmask = cv2.bitwise_and(gmask, smask)

        red = cv2.bitwise_or(cv2.inRange(hue, 0, 10), 
            cv2.inRange(hue, 170, 180))
        rmask = cv2.bitwise_and(red, fgmask)
        rsmask = cv2.bitwise_and(rmask, smask)

        bestGreens = list(brightest(BGsubtract, N, gsmask))
        bestReds = list(brightest(BGsubtract, N, rsmask))
        bestReds = [r for r in bestReds if minDist(r, bestGreens) <= MAX_SEP] if bestGreens else []
        bestGreens = [g for g in bestGreens if minDist(g, bestReds) <= MAX_SEP] if bestReds else []

        # Haoyu: rats can not "jump"
        if n==1:
            same=0
        if same < SAME and n > 10 and  pow(bestGreens[0][0]-pregreen[0][0],2)+pow(bestGreens[0][1]-pregreen[0][1],2) > JUMP:
            bestGreens=pregreen
        if same < SAME and n > 10 and pow(bestReds[0][0]-prered[0][0],2)+pow(bestReds[0][1]-prered[0][1],2) > JUMP:
            bestReds=prered
        if n>10 and bestReds==prered:
            same=same+1
        else:
            same=0
        prered=bestReds
        pregreen=bestGreens
        yield (bestReds, bestGreens)
        #print bestReds
        #print bestGreens



def findCenters(data):

    """
    For the (redPoint, greenPoint), finds the center of the two LED's and returns them as (x, y) coords
    """

    nopoint = ([], [])

    Centers = []

    def centroid(point):
        (pt1, pt2) = point
        x = (pt1[0] + pt2[0])/2
        y = (pt1[1] + pt2[1])/2
        return (x, y)

    for (r, g) in data:
        if (r, g) == ([], []):
            Centers.append(nopoint)
        else:
            point = (r[0], g[0])
            Centers.append(centroid(point))
    return Centers

def writeCSV(data):
    with open('coords.csv', 'wb') as csvfile:
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
        cv2.setTrackbarPos(num, 'frame', n)
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
        


def simpleInterpolate(data):

    """
    A function to remove outliers and interpolate empty frames from using the surrounding frames
    """

    EMPTY = object()
    nopoint = EMPTY

    def findEmpty(data):
        noEmpty = []
        for point in data:
            if point == ([], []):
                noEmpty.append(nopoint)
            else:
                noEmpty.append(point)
        return noEmpty

    def findOutliers(data):
        """
        Finds points that deviate too far from the norm and removes them, "too far" defined
        roughly has moving too far from the last known point as a function of how many empty
        points exist between the current frame and the frame of the last known point.
        """
        noOutliers = []
        lastPoint = data[0]
        lastKnown = 0

        for point in data:

            if point is EMPTY:
                lastKnown += 1
                noOutliers.append(nopoint)
            else:
                if dist(lastPoint, point) > ((lastKnown ** 0.5)/2 * MAX_EXPECTED_MOVEMENT) or \
                    dist(lastPoint, point) > (lastKnown * EXPECTED_MOVEMENT): #This might need to be reworked...
                    noOutliers.append(nopoint)
                    lastKnown += 1
                else:
                    lastPoint = point
                    noOutliers.append(lastPoint)
                    lastKnown = 0

        return noOutliers

    def interpolate(pt1, pt2, Length, preInterpolate):
        Length = Length + preInterpolate - 1
        x = (preInterpolate * (pt2[0] - pt1[0])/Length) + pt1[0]
        y = (preInterpolate * (pt2[1] - pt1[1])/Length) + pt1[1]
        newPt = (x, y)
        return newPt

    def bookend(data):
        # I need to ensure that the first and last points are not EMPTY for
        # fillEmpty() to function properly

        newData = []
        firstPoint = data[0]
        index = 1
        while firstPoint == EMPTY:
            firstPoint = data[index]
            index += 1

        newData.append(firstPoint)

        for i in range(1,len(data)-2):
            newData.append(data[i])

        lastPoint = data[len(data)-1]
        index = len(data)-2
        while lastPoint ==EMPTY:
            lastPoint = data[index]
            index -= 1

        newData.append(lastPoint)

        return newData

    def fillEmpty(data):

        newData = []

        for i in range(1,len(data)-2):
            point = data[i]
            newPoint = point
            pPoint = data[i-1]
            nPoint = data[i+1]
            if point is EMPTY:
                runLength = 1
                while nPoint is EMPTY:
                    nPoint = data[i+runLength]
                    runLength += 1
                preInterpolate = 1
                while pPoint is EMPTY:
                    pPoint = data[i-preInterpolate]
                    preInterpolate += 1
                newPoint = interpolate(pPoint, nPoint, runLength, preInterpolate)

        return newData

    data = list(findEmpty(data))
    data = list(bookend(data))
    data = list(findOutliers(data))
    data = list(bookend(data))

    return fillEmpty(data)


def processVideo(f):
    print("Processing frames...")
    pts = list(candidatePoints(f))
    print("Done processing. Interpolating path...")
    data = list(findCenters(pts))
    reviewCoords(data, f)
    #by Jiaqi and Haoyu
    #data = list(simpleInterpolate(data))
    writeCSV(data)

def run():
    for vid in sys.argv[1:]:
        processVideo(vid)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()

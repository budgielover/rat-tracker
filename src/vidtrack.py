#!/usr/bin/env python
#
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
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(frame, None)
        yield maxLoc        
        frame[maxLoc[1], maxLoc[0]] = 0 # so it won't be found next


def interpolate(x, y, alpha):
	"""
	interpolate data point
	"""
    return x * (1 - alpha) + y * alpha

def dist(pt1, pt2):
	"""
	Returns distance between pt1 and pt2
	"""
    dx = pt1[0] - pt2[0]
    dy = pt1[1] - pt2[1]
    return sqrt(dx**2 + dy**2)

def minDist(pt, pts):
	"""
	Returns closest point
	"""
    return min(dist(pt, p) for p in pts)


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

        #rats can not "jump"
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
	"""
	Writes data to CSV file called coords.csv
	"""
    with open('coords.csv', 'wb') as csvfile:
        coordwriter = csv.writer(csvfile)
        for x, y in data:
            coordwriter.writerow([x, y])
        

def processVideo(f):
	"""
	Routine to get from video points and write to CSV
	"""
    print("Processing frames...")
    pts = list(candidatePoints(f))
    print("Done processing. Interpolating path...")
    data = list(findCenters(pts))
    writeCSV(data)

def run():
    for vid in sys.argv[1:]:
        processVideo(vid)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run()

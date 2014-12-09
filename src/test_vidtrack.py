import vidtrack
import cv2
import cv2.cv
import numpy
from numpy import unravel_index
import sys
import reviewCoords

#please copy the test.avi into the same directory of the code

#please click on the screen randomly when test the GUI(to rewrite the data), and after you see "pytest-qt-1.2.2/pytestqt/_tests/test_basics.py .....", close the interface by hand
#def test_reviewCoords():
#    file='testgreen.avi'
#    data=[(351,229),(506,333),(185,146)]
#    reviewCoords.reviewCoords(data,file)
#    assert data!=[(351,229),(506,333),(185,146)]

def test_brightest():
    frame=numpy.mat([[7,2,3],[2,3,4],[3,4,5]])
    assert list(vidtrack.brightest(frame,1))==[(0,0)]

def test_interpolate():
    assert vidtrack.interpolate(1,2,0.5)==1.5

def test_dist():
    assert vidtrack.dist((0,1),(3,5))==5

def test_mindist():
    assert vidtrack.minDist((0,1),[(3,5),(7,9),(1,1)])==1

def test_findCenters():
    assert vidtrack.findCenters([([(0, 1)], [(2, 9)])])==[(1,5)]


def test_writeCSV(tmpdir):
    data=[(1,5),(2,10)]
    file = tmpdir.join('output.txt')
    vidtrack.writeCSV(data,file.strpath)
    assert file.read() == '1,5\r\n2,10\r\n'

def test_writeCSV(tmpdir):
    data=[(1,5),(2,10)]
    file = tmpdir.join('output.txt')
    reviewCoords.writeCSV(data,file.strpath)
    assert file.read() == '1,5\r\n2,10\r\n'


def test_frames(tmpdir):
    file='test.avi'
    k=0
    for n, total, frame in vidtrack.frames(file):
        k=k+1
        assert total==3
        assert n==k
        assert frame.shape==(480,720,3)

def test_findBackground():
    file='test.avi'
    assert vidtrack.findBackground(file,0.01).shape==(480,720)
    assert vidtrack.findBackground(file,0.01)[1][1]==0

def test_candidatePoints():
    file='test.avi'
    assert list(vidtrack.candidatePoints(file,0))==[([(351,229)],[(351,229)]),([(506,333)],[(506,333)]),([(185,146)],[(185,146)])]

def test_findwithcandidate():
    file='test.avi'
    pts = list(vidtrack.candidatePoints(file,0))
    data = list(vidtrack.findCenters(pts))
    assert data==[(351,229),(506,333),(185,146)]

def test_systemvid(tmpdir):
    file='test.avi'
    pts = list(vidtrack.candidatePoints(file,0))
    data = list(vidtrack.findCenters(pts))
    file = tmpdir.join('output.txt')
    vidtrack.writeCSV(data,file.strpath)
    assert file.read() == '351,229\r\n506,333\r\n185,146\r\n'

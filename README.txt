This is an introduction to the rat-tracker software created by Arjun Patel, Haoyu Zhang, Jiaqi Zheng, and Hana Qoronfleh for Emory University’s Manns lab. 

Software Requirements
==================

The rat-tracker program requires:

Operating System: Mac OS X or later or Ubuntu 12.0 or later
Language: any Python 2.7*
Software Dependencies: Open CV 2.4.9
		       numpy
Optional: 
Sphinx 1.2.3


 
Installation guide for Open CV
=============

Mac: If you have not installed Homebrew already, follow the instructions at http://brew.sh/ and install. 
Then run the following commands in the terminal :

Brew tap homebrew/science
Brew install opencv --with-fmpeg --with-qt

Linux/Unix: 

Follow the instructions at http://www.samontab.com/web/2014/06/installing-opencv-2-4-9-in-ubuntu-14-04-lts/



Installation guide for Sphinx
=====================
Sphinx is an auto-documentation tool that that can automatically create documentation files from the docstrings present in the program. It is not necessary to download it unless you wish to change the documentation. It can be downloaded at https://pypi.python.org/pypi/Sphinx or by running the following command in the terminal:

easy_install -U Sphinx

Then run:

sudo python setup.py

You will need root access to install this. This will let you choose the name of the project, what directory the commendation is installed in, and other setup options. It’s recommended that the autodoc setting is set to yes. For more information, view the Sphinx website at http://sphinx-doc.org/index.html. 

To actually create the documentation, run:

sphinx-apidoc  -o outputdir packagedir 

This generates rst files. Outputdir is the location of the outputted files and packagedir is the path to the files you wish to document. For more command-line options, see http://sphinx-doc.org/invocation.html#invocation.

 To create html files from your rst files, run:

sphinx-build sourcedir builddir 

Sourcedir is the source directory and builder is where you wish to place your files. For more command-line options, see http://sphinx-doc.org/invocation.html#invocation.

Installation guide for Scripts
===============================
To install the scripts globally, simply run python setup.py install

Tutorial
===========
The rat-tracker program is a command-line utility that allows a user to input a video file, receive and outputted file contacting the coordinates of the rat, and review the video and correct any mistakes in the coordinate locations. There are two scripts in the rat-tracker program. The first, vidtrack.py, finds the rat’s location and outputs a file containing the coordinates. The second, reviewCoords.py, opens a GUI and allows the user to go over each frame and change the coordinates. 

To run vidtrack.py, enter:

python vidtrack.py inputfile.avi [inputfile2.avi..] OPTIONS

Command Line Options:

-h, help: displays a brief description of all command-line options in terminal window
--write csv, --write txt: choose the output file format. Default is csv.
-v or --verbose: while program is running, terminal output displays percent of frames complete. Default is off.

To run reviewCoords.py, enter:

python reviewCoords.py coords.csv inputfile.avi

where coords.csv is the csv file output from vidtrack.py and inputfile.avi is the corresponding video. 

GUI Instructions:

To move frame by frame through the video, hit any key on the keyboard. To change a coordinate, click the spot you wish to change the coordinate to and hit ENTER. To move to a specific frame, click the track bar and type the number of the frame you want to move to into the box and hit ENTER. You can also click and drag the track bar and hit ENTER to change slides. To exit, hit the escape key. For help within the GUI, type h. 

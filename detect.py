#!/usr/bin/python
"""
This program is demonstration for face and object detection using haar-like features.
The program finds faces in a camera image or video stream and displays a red box around them.

Original C implementation by:  ?
Python implementation by: Roman Stanchak, James Bowman
"""
import sys
import cv
from optparse import OptionParser

# Parameters for haar detection
# From the API:
# The default parameters (scale_factor=2, min_neighbors=3, flags=0) are tuned 
# for accurate yet slow object detection. For a faster operation on real video 
# images the settings are: 
# scale_factor=1.2, min_neighbors=2, flags=CV_HAAR_DO_CANNY_PRUNING, 
# min_size=<minimum possible face size

min_size = (20, 20)
image_scale = 2
haar_scale = 1.2
min_neighbors = 2
haar_flags = 0

def detect_and_draw(imgage, i_path, cascade, c_name, c_color):
    r, g, b = c_color
    # allocate temporary images
    gray = cv.CreateImage((imgage.width,imgage.height), 8, 1)
    small_img = cv.CreateImage((cv.Round(image.width / image_scale),
			       cv.Round (image.height / image_scale)), 8, 1)

    # convert color input image to grayscale
    cv.CvtColor(image, gray, cv.CV_BGR2GRAY)

    # scale input image for faster processing
    cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)

    cv.EqualizeHist(small_img, small_img)

    if(cascade):
        t = cv.GetTickCount()
        faces = cv.HaarDetectObjects(small_img, cascade, cv.CreateMemStorage(0),
                                     haar_scale, min_neighbors, haar_flags, min_size)
        t = cv.GetTickCount() - t
        print "detection time = %gms" % (t/(cv.GetTickFrequency()*1000.))
        if faces:
            for ((x, y, w, h), n) in faces:
                # the input to cv.HaarDetectObjects was resized, so scale the 
                # bounding box of each face and convert it to two CvPoints
                pt1 = (int(x * image_scale), int(y * image_scale))
                pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
                cv.Rectangle(image, pt1, pt2, cv.RGB(r, g, b), 3, 8, 0)

    cv.SaveImage(i_path, image)

if __name__ == '__main__':

    c_path = '/usr/local/share/opencv/haarcascades/'

    c_list = [('haarcascade_frontalface_default.xml', (72,61,139)),
              ('haarcascade_frontalface_alt.xml', (255, 0, 0)),
              ('haarcascade_frontalface_alt2.xml', (0, 255, 0)),
              ('haarcascade_frontalface_alt_tree.xml', (0, 0, 255)),
              ('haarcascade_profileface.xml', (127,255,0))]

    #  try:
    c_list = c_list[:int(sys.argv[2])]
    #    except:
    #       list = list

    i_path = sys.argv[1]
    image = cv.LoadImage(i_path, 1)
    
    for c_name, c_color in c_list:
        print c_path+c_name
    	cascade = cv.Load(c_path+c_name)
        detect_and_draw(image, i_path, cascade, c_name, c_color)


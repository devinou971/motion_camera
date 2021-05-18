#!/usr/bin/python3

import cv2
import numpy as np
import time
import datetime
import sys
from optparse import *
from threading import Thread

max_frames_for_reference = 10
threshold = 50
show_camera = False
keypress = ""



def set_key_pressed():
    global keypress
    while keypress.lower() != "q" :
        keypress = input()
        time.sleep(0.001)


t = Thread(target=set_key_pressed)
t.daemon = True
t.start()

parser = OptionParser()


def show_camera_feed(option, opt_str, value, parser):
    global show_camera
    show_camera = True


parser.add_option("-c",
                  "--camera_index",
                  help="Index of the camera from 0 to 9",
                  metavar="INDEX",
                  dest="camera_index",
                  default=None)

parser.add_option("-d",
                  "--duration_offset",
                  help="Duration of video in sec after last movement detected",
                  metavar="SEC",
                  dest="duration_offset",
                  default=10)

parser.add_option("-s",
                  "--show",
                  help="It shows the different feed from the camera onto your screen",
                  action="callback",
                  callback=show_camera_feed)

(options, args) = parser.parse_args()

# Catch the errors from the arguments in the command line
camera_index = options.camera_index

if camera_index is not None:
    try:
        camera_index = int(options.camera_index)
        if 0 <= camera_index <= 9:
            cam = cv2.VideoCapture(camera_index)
            if not (cam.isOpened()):
                raise OptionValueError("This camera index isn't valid")
            cam.release()
        else:
            raise ValueError()

    except ValueError:
        raise OptionValueError("The camera index must be a number between 0 and 9")


try:
    duration_offset = int(options.duration_offset)
except ValueError:
    raise OptionValueError("The duration offset must be a number")

if camera_index is None:
    for i in range(10):
        cam = cv2.VideoCapture(i)
        if cam.isOpened():
            print("Using camera at index {}".format(i))
            camera_index = i
            cam.release()
            break
        cam.release()
    if camera_index is None:
        raise Exception("No camera found")

# Setup the camera feed
stream = cv2.VideoCapture(camera_index)
valid, image = stream.read()
video_frames = []

print("Camera {} found".format(camera_index), "\nPress q and Enter to quit the program")

# We set a number of reference frames
references = np.array([image.copy().astype(np.uint64) for i in range(max_frames_for_reference)])

reference_index = 0

# We setup the videoBuilder
start_vid = False
time_start = 0
videoBuilder = cv2.VideoWriter()

while valid is True:
    valid, image = stream.read()
    if valid is False:
        
        raise ValueError("The camera has not been found")
    imgBin = image.copy()

    # This section is used to create the reference image

    # At first we add the new image to the frame collection 
    references[reference_index] = image.copy()
    reference_index = reference_index + 1 if reference_index < references.shape[0] - 1 else 0

    # And then we just take the average image for reference
    reference = image.copy()
    for j in references:
        reference = reference + j
    reference = reference / (max_frames_for_reference + 1)
    reference = reference.astype(np.uint8)

    if not (reference is None):

        imgDiff = np.abs(image.astype(np.int16) - reference.astype(np.int16))
        imgBin = imgDiff > threshold

        colored_img = imgBin.astype(np.uint8) * 255

        grey_img = np.sum(colored_img.astype(np.uint8), axis=-1) > 1
        grey_img = grey_img.astype(np.uint8) * 255

        mean = np.mean(grey_img)

        # Here we begin to record if the mean is higher than 10
        if mean >= 10.0:
            # If the record just started, we want to setup the videoBuilder correctly
            if start_vid is False:
                local_time = time.localtime()
                file_name = "{}_{}_{}_{}_{}_{}.avi".format(local_time.tm_mday, local_time.tm_mon, local_time.tm_year,
                                                           local_time.tm_hour, local_time.tm_min, local_time.tm_sec)
                fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
                w = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT))

                print("Building Video :", file_name)

                videoBuilder = cv2.VideoWriter(file_name, fourcc, cv2.CAP_PROP_FPS, (w, h))

                start_vid = True
            time_start = time.time()

        if start_vid:
            # In every frame of the video, we want the date printed onto the frame
            font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
            dt = str(datetime.datetime.now())
            frame = cv2.putText(image, dt, (10, 50), font, 1, (0, 0, 255), 4, cv2.LINE_8)

            videoBuilder.write(frame)

            # We stop the recording if we don't detect motion during a set number of seconds 
            if time.time() - time_start >= duration_offset:
                start_vid = False
                videoBuilder.release()
        if show_camera:
            cv2.imshow("Motion camera", grey_img)

    if show_camera:
        cv2.imshow("Reference", reference)
        cv2.imshow("Camera", image)

    # We quit the program if the "q" key is pressed
    if cv2.waitKey(4) & 0xFF == ord('q') or keypress.lower() == "q":
        videoBuilder.release()
        break
sys.exit(0)
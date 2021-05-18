# Motion Camera in python

## Requirements : 

If you want to use this program on  your machine, you'll need to install Opencv-Python and Numpy.

I used the 4.5.1.48 version of Opencv-Python and the 1.20.1 version of Numpy.

## How to use it

This script is catching the motion in the room and saving it into a video named with the date in it.


### The parameters 

It has 3 main options that you can change : 

- The duration of the video after the movement stopped can be changed by adding the `` -d SEC`` or `` --duration=SEC `` parameter when launching from command line. 
By default, the duration is 10sec.
  

- The camera index is also something you can tweak. Opencv supports 10 different slots of cameras ranging from 0 to 9. Giving a value can be useful if you want to use an usb camera instead of a built-in camera.
You can change the camera index by using the `` -c INDEX `` or `` --camera_index=INDEX `` parameter when launching from command line.
  

- The last parameter that you can add is the "show" option (`` -s `` or `` --show ``) this option lets you show 3 video feed on your screen, At first, you see the normal camera, the reference and finally the motion camera.

### Example of use

This command :\
`` python3 main.py -c 0 -d 10 --show ``\
Is going to launch the program with the default webcam of your PC, the duration after motion will be set to 10 seconds and 3 video feeds will appear on your screen



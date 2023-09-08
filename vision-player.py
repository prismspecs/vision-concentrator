import cv2
import time
import os
# import pyautogui

widow_name = "window"
videoFileName = "output/all_visions.mp4"

# get directory from current_config.dat
with open("current_config.dat", "r") as f:
    project_dir = f.read()

videoFileName = os.path.join(project_dir, "all_visions.mp4")

# Hide the cursor
# pyautogui.FAILSAFE = False
# pyautogui.moveTo(3000, 3000)

# Loop for playing video in repeat model
while True:

    isClose = False
    video = cv2.VideoCapture(videoFileName)
    # Set Video Frame to Full Screen
    cv2.namedWindow(widow_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(
        widow_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.moveWindow(widow_name,1600,0)

    # wait until video file is loaded
    while (video.isOpened() == False):
        video = cv2.VideoCapture(videoFileName)
        cv2.waitKey(1000)
    
    # Loop for Reading Video Frame
    while (True):
        ret, frame = video.read()
        if (ret == True):
            cv2.imshow(widow_name, frame)
            # Esc button(27) to exit the video
            if (cv2.waitKey(1) == 27):
                isClose = True
                break
        else:
            break
    
        time.sleep(1 / 8)

    # Close Repeat Video Loop
    if (isClose):
        break
# Release video and destory frame after ESC press
video.release()
cv2.destroyAllWindows()

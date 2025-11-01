# import required libraries
import dxcam
import cv2

# open video stream with default parameters
camera = dxcam.create()
camera.start(video_mode=True, target_fps=60)
while True:
    # read frames from stream
    frame = camera.get_latest_frame()
    # check for frame if Nonetype

    # {do something with the frame here}

    # Show output window
    cv2.imshow("Output Frame", frame)
    # check for 'q' key if pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
# close output window
cv2.destroyAllWindows()
# safely close video stream
camera.stop()


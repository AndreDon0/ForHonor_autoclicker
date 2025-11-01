import time
from threading import Thread
import cv2
import dxcam
import pyautogui as pag
from win32api import GetSystemMetrics
#width = GetSystemMetrics(0)
#height = GetSystemMetrics(1)
#fps = 60
#camera = dxcam.create()
#camera.start(target_fps=fps, video_mode=True)
#writer = cv2.VideoWriter(
#    "video.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
#)
#for i in range(120):
#    writer.write(camera.get_latest_frame())
#camera.stop()
#writer.release()


class Record_Video:
    def __init__(self, name="video.mp4", camera_create=True, fps=60) -> None:
        self.width = GetSystemMetrics(0)
        self.height = GetSystemMetrics(1)
        self.fps = fps
        if camera_create:
            self.camera_for_video = dxcam.create(output_color="BGR")
            self.camera_for_video.start(target_fps=fps, video_mode=True)
        else:
            self.camera_for_video = camera
        self.show_window = False
        self.start_record = False
        self.circle_threads = []
        self.writer = cv2.VideoWriter(name, cv2.VideoWriter_fourcc(*"mp4v"), fps, (self.width, self.height))

    def create_window(self, name="Live", width_window=480, height_window=300):  # Not working
        self.show_window = True
        self.window_name = name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, width_window, height_window)

    def start(self):
        self.start_record = True
        self.__thread = Thread(target=self.Video_Recording, daemon=True)
        self.__thread.start()

    def Video_Recording(self):
        while self.start_record:
            self.__frame = self.camera_for_video.get_latest_frame()
            self.start_changing = True

            self.writer.write(self.__frame)
            if self.show_window:
                cv2.imshow(self.window_name, self.__frame)

    def stop_and_save(self):
        self.start_record = False
        self.writer.release()
        if self.show_window:
            cv2.destroyWindow(self.window_name)

    def circle_and_sign(self, region_circle, text="", allways=False):
        if allways:
            tread = Thread(self.circle_and_sign_allways, args=(self, region_circle, text, len(self.circle_threads)), daemon=True)
            self.circle_threads.append(True)
            tread.start()
        else:
            tread = Thread(self.circle_and_sign_one, args=(self, region_circle, text, len(self.circle_threads)), daemon=True)
            self.circle_threads.append(True)
            tread.start()

    def circle_and_sign_one(self, region_circle, text="", namber=0):
        while not self.start_changing and self.circle_threads[namber]:
            pass
        self.__rect = cv2.rectangle(self.__frame, (region_circle[0], region_circle[1]),
                                   (region_circle[0] + region_circle[2], region_circle[1] + region_circle[3]),
                                   (0, 0, 255), 5)
        self.__text = cv2.putText(self.__frame, text, (region_circle[0], region_circle[1] + region_circle[3] + 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        self.circle_threads[namber] = False

    def circle_and_sign_allways(self, region_circle, text="", namber=0):
        while True:
            while not self.start_changing and self.circle_threads[namber]:
                pass
            self.__rect = cv2.rectangle(self.__frame, (region_circle[0], region_circle[1]),
                                       (region_circle[0] + region_circle[2], region_circle[1] + region_circle[3]),
                                       (0, 0, 255), 5)
            self.__text = cv2.putText(self.__frame, text, (region_circle[0], region_circle[1] + region_circle[3] + 20),
                                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            self.circle_threads[namber] = False

rec = Record_Video()
rec.start()
width, height = pag.size()
REGION = [width // 9 * 4, height // 3, width // 6, height // 4]
rec.circle_and_sign(REGION, text="adsasd", allways=True)
time.sleep(2)
rec.stop_and_save()
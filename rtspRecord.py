import cv2
from threading import Thread, Event
import time
import os
from datetime import datetime

camera_ip_list = ['192.168.2.74', '192.168.2.100']
IF_STOP = False
TIMEOUT = 15 * 60  # mins


class Camera:
    def __init__(self, cap, video_writer, thread, event):
        self.cap = cap
        self.video_writer = video_writer
        self.thread = thread
        self.event = event


class RTSPRecord(Thread):
    def __init__(self, folder_path):
        self.camera_list = []
        self.folder_path = folder_path
        Thread.__init__(self)
        # self.videoLength = video_length

    def run(self):
        for camera_ip in camera_ip_list:
            video_name = self.video_namer(camera_ip)
            cap = self.set_cap(camera_ip)
            video_writer = self.set_video_writer(cap, video_name)
            event = Event()
            thread = Thread(target=self.record_video, args=(cap, video_writer,))
            # self.thread_list.append([thread], event)
            self.camera_list.append(Camera(cap, video_writer, thread, event))
            thread.start()

        while not IF_STOP:
            time.sleep(1)

        self.end_process()

    def end_process(self):
        for camera_obj in self.camera_list:
            camera_obj.cap.release()
            camera_obj.video_writer.release()
            camera_obj.thread.join()
            if camera_obj.thread.is_alive():
                camera_obj.event.set()  # set the event
                print("thread is not done, setting event to kill thread.")
            else:
                print("thread has already been killed")

    @staticmethod
    def video_namer(camera_ip):
        return camera_ip

    @staticmethod
    def record_video(cap, video_writer):
        global IF_STOP
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                video_writer.write(frame)
            if IF_STOP:
                break

    @staticmethod
    def set_cap(camera_ip):
        cap = cv2.VideoCapture("rtsp://admin:123456@" + camera_ip + "/554/ch01_sub.264")
        return cap

    # @staticmethod
    def set_video_writer(self, cap, VideoName):
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'MP42')  # cv2.VideoWriter_fourcc() does not exist
        video_writer = cv2.VideoWriter(
            self.folder_path + "\\" + self.folder_path.split("\\")[-1] + "-" + VideoName + ".avi", fourcc, 25, (w, h))

        return video_writer


def create_folder(folder_name):
    path = os.path.join(os.getcwd(), folder_name)
    if os.path.exists(path):
        print("The folder with the same name is already exist please indicate different time of day and rerun")
        exit()
    else:
        os.mkdir(path)
    print("FOLDER CREATE : ", path)
    return path


if __name__ == '__main__':
    timeofday = input("PLEASE INDICATE TIME OF DAY : ")
    date = datetime.today().strftime('%Y-%m-%d')
    folder_path = create_folder(date + "-" + timeofday)
    time_start = time.time()
    rtsp_record = RTSPRecord(folder_path)
    rtsp_record.start()
    print("RTSP Recorder connected")
    print("Please press ctrl + c to end process")
    print("otherwise process will be terminate in 1 hour")
    try:
        while True:
            time_now = time.time()
            if (time_now - time_start >= TIMEOUT):
                IF_STOP = True
                break
            time.sleep(2)
            print("PROCESS : Recording")
    except KeyboardInterrupt:
        IF_STOP = True
        rtsp_record.end_process()
        print("Process has been terminated")

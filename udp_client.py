from __future__ import division
import cv2
import numpy as np
import socket
import struct
import math
from PIL import ImageGrab
import time
import win32gui, win32ui, win32con#
import dxcam

def get_screenshot():
    # define your monitor width and height
    w, h = 1920, 1080

    # for now we will set hwnd to None to capture the primary monitor
    #hwnd = win32gui.FindWindow(None, window_name)
    hwnd = None

    # get the window image data
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (w, h), dcObj, (0, 0), win32con.SRCCOPY)

    # convert the raw data into a format opencv can read
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (h, w, 4)

    # free resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())

    # drop the alpha channel to work with cv.matchTemplate()
    img = img[...,:3]

    # make image C_CONTIGUOUS to avoid errors with cv.rectangle()
    img = np.ascontiguousarray(img)

    return img

class FrameSegment(object):
    """ 
    Object to break down image frame segment
    if the size of image exceed maximum datagram size 
    """
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64 # extract 64 bytes in case UDP frame overflown
    def __init__(self, sock, port, addr="127.0.0.1"):
        self.s = sock
        self.port = port
        self.addr = addr
        self.quality = 80
    def udp_frame(self, img):
        """ 
        Compress image and Break down
        into data segments 
        """
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        compress_img = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, int(self.quality)])[1]
        #compress_img = cv2.imencode(".webp",img,[cv2.IMWRITE_WEBP_QUALITY, 50])[1]
        dat = compress_img.tobytes()
        size = len(dat)
        count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
        array_pos_start = 0
        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            self.s.sendto(struct.pack("B", count) +
                dat[array_pos_start:array_pos_end], 
                (self.addr, self.port)
                )
            array_pos_start = array_pos_end
            count -= 1


def main():
    """ Top level main function """
    # Set up UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 12345

    fs = FrameSegment(s, port)

    # define dimensions of screen w.r.t to given monitor to be captured
    #options = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
    camera = dxcam.create(output_idx=0, output_color="BGR")
    camera.start(target_fps=100, video_mode=True)
    #cap = cv2.VideoCapture(camera)
    # open video stream with defined parameters
    #stream = ScreenGear(logging=False, **options).start()
    #cap = cv2.VideoCapture('udp://127.0.0.1:55555',cv2.CAP_FFMPEG)
    while True:
        start = time.perf_counter()
        #print(resize)
        #img = ImageGrab.grab(bbox=(0, 0, 1920, 1080)) #x, y, w, h
        frame = camera.get_latest_frame()
        #img_np = np.array(img)
        #frame = stream.read()       
        try:
            #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frame = get_screenshot()
        #_,frame = cap.read()
            frame = cv2.resize(frame, (1280,720))
            #cv2.imshow("asd",frame)
            fs.udp_frame(frame)
        except:
            continue
        end = time.perf_counter()
        total_time = end - start
        fps = 1 / total_time
        print('fps: ',fps)
        cv2.waitKey(1)
if __name__ == "__main__":
    main()
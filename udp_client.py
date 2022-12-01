from __future__ import division
import cv2
import socket
import struct
import math
import time
import dxcam

class FrameSegment(object):
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64 # extract 64 bytes in case UDP frame overflown
    def __init__(self, sock, port, addr="IPADDRESS_HERE"):
        self.s = sock
        self.port = port
        self.addr = addr
        self.quality = 60
    def udp_frame(self, img):
        compress_img = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, int(self.quality)])[1]
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
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 55555
    fs = FrameSegment(s, port)
    camera = dxcam.create(output_idx=0, output_color="BGR")
    camera.start(target_fps=100, video_mode=True)
    while True:
        start = time.perf_counter()
        frame = camera.get_latest_frame()
        try:
            frame = cv2.resize(frame, (1280,720))
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

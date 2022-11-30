from __future__ import division
import cv2
import numpy as np
import socket
import struct
import time

MAX_DGRAM = 2**16

def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        print(seg[0])
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finish emptying buffer")
            break

def main():
    """ Getting image udp frame &
    concate before decode and output image """
    
    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', 12345))
    dat = b''
    dump_buffer(s)

    while True:
        #start = time.perf_counter()
        seg, addr = s.recvfrom(MAX_DGRAM)
        if struct.unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]
            img = cv2.imdecode(np.frombuffer(dat, dtype=np.uint8), 1)
            img = cv2.resize(img, (1920,1080))
            #end = time.perf_counter()
            #total_time = end - start
            #fps = 1 / total_time
            #cv2.putText(img, f'FPS: {int(fps)}', (20,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.imshow('frame', img)
            cv2.waitKey(1)
            dat = b''

if __name__ == "__main__":
    main()
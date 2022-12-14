from __future__ import division
import cv2
import numpy as np
import socket
import struct
import time
import pygame

MAX_DGRAM = 65536

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

    screen = pygame.display.set_mode(
    (1920, 1080),
    pygame.FULLSCREEN
    )
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 55555))
    dat = b''
    dump_buffer(s)

    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        if struct.unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]
            img = cv2.imdecode(np.frombuffer(dat, dtype=np.uint8), 1)
            try:
                cv2.flip(img,1,img)
                img = cv2.resize(img, (1920,1080))
                frame=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                frame=np.rot90(frame)
                frame=pygame.surfarray.make_surface(frame)
                #cv2.imshow('frame', img)
                screen.blit(frame,(0,0))
                pygame.display.flip()
            except:
                pass
            dat = b''
            cv2.waitKey(16)

if __name__ == "__main__":
    main()

import sys

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()
#import keyboard

from pynput import keyboard

def tmp(q, buff):
    #while True:
    #    if keyboard.is_pressed('q'):
    #        q.put('pressed!')
    while True:
        ch = sys.stdin.read(1)
        if ch == '\n':
            q.put(buff[0])
            buff[0] = ''
        else:
            buff[0] += ch
        

        #with keyboard.Events() as events:
            # Block for as much as possible
        #    event = events.get(1e6)

        #    print(type(event).__name__)
            #while(event.
            #if event.key == keyboard.KeyCode.from_char('s'):
            #    print("YES")
            #print(event.key)
            #q.put(event.key)
        #    print(event.key.char)
        #print(ch)
        #q.put(ch)
    #q.put(getch())
    #q.put('test')

#ch = getch()
#print(ch)

import multiprocessing as mp
import threading
import queue
import time
from multiprocessing import Process, Manager, Value
from ctypes import c_char_p

#erase = '\x1b[1A\x1b[2K'
def tmp2(string):
    #print('', end='')
    time.sleep(1)
    print(string.value)
    print('\rthisisatest')
    print(string.value)

if __name__ == '__main__':
    manager = Manager()
    string = manager.Value(c_char_p, "")
    #p = mp.Process(target=tmp2, args=[string])
    #p.start()

    while True:
        print('ttttt')
        ch = sys.stdin.read(1)
        print(ch)
        if ch == '\n':
            print(string.value)
            string.value = ''
        else:
            string.value = string.value + ch
            print(string.value)

    #q = queue.Queue()
    #proc = threading.Thread(target=tmp, args=[q, gbuff])
    #proc.daemon = True
    #proc.start()
    #while True:
    #    print(q.get())
    #proc.join()
    #p.join()

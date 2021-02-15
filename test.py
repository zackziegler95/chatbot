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

def tmp(q):
    #while True:
    #    if keyboard.is_pressed('q'):
    #        q.put('pressed!')
    while True:
        #ch = sys.stdin.read(1)
        ch = getch()
        print(ch)
        q.put(ch)
    #q.put(getch())
    #q.put('test')

#ch = getch()
#print(ch)

import multiprocessing as mp
import threading
import queue


if __name__ == '__main__':
    q = queue.Queue()
    proc = threading.Thread(target=tmp, args=[q])
    proc.daemon = True
    proc.start()
    while True:
        print(q.get())
    proc.join()

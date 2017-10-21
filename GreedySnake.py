import threading
import time
import sys
import random


is_terminated = False

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


class Snake(object):
    dirct_code = {0:(-1,0), 1:(1,0), 2:(0,-1), 3:(0,1)}
    def __init__(self, L = 5, n = 30,m = 30):
        self.L = L
        self.n = n
        self.m = m
        # tail --> head
        self.pos = [[3,i+3] for i in range(self.L)]
        # up->(-1,0) down->(1,0) left->(0,-1) right->(0,1)
        self.__dirct = (0,1)
        self.new_apple = [random.randint(0, self.n-1),random.randint(0, self.m-1)]
        self.eaten_apple = []

    def change_dirct(self, ctr):
        if self.__dirct == (0, 1) or self.__dirct == (0, -1):
            if ctr == 0 or ctr == 1:
                self.__dirct = Snake.dirct_code[ctr]
        else:
            if ctr == 2 or ctr == 3:
                self.__dirct = Snake.dirct_code[ctr]

    def is_dead(self):
        u = self.pos[-1][0] == self.n
        d = self.pos[-1][0] == -1
        l = self.pos[-1][1] == -1
        r = self.pos[-1][1] == self.m
        suicide = self.pos[-1] in self.pos[:-1]
        return u or d or l or r or suicide

    def run(self):
        global is_terminated
        while True:
            if is_terminated:
                return
            if self.new_apple == self.pos[-1]:
                self.eaten_apple.append(self.new_apple)
                self.new_apple = [random.randint(0, self.n-1),random.randint(0, self.m-1)]
                while self.new_apple in self.pos:
                    self.new_apple = [random.randint(0, self.n-1),random.randint(0, self.m-1)]
            
            if len(self.eaten_apple) != 0 and self.eaten_apple[0] == self.pos[0]:
                self.eaten_apple.pop(0)
            else:
                self.pos.pop(0)

            new_head = [self.pos[-1][i]+self.__dirct[i] for i in range(2)]
            self.pos.append(new_head)
            if self.is_dead():
                is_terminated = True
                return
            self.draw()
            time.sleep(.1)


    def draw(self):
        grid = [[0 for _ in range(self.m)] for _ in range(self.n)]
        for pos in self.pos:  
            grid[pos[0]][pos[1]] = 1
        grid[self.new_apple[0]][self.new_apple[1]] = 2

        cm = {0:"\033[00;20m- \033[00m", 1:"\033[01;32mO \033[00m", 2:"\033[01;31mO \033[00m"}
        color = lambda x: cm[x]
        lines = ""
        for i in range(self.n):
            lines += str.join("", list(map(color, grid[i]))) + "\n\r"
        print(lines, end="")
        print('\033[{}A'.format(self.n+1))


def ctr(snake):
    global is_terminated
    while True:
        if is_terminated:
            return
        ch = getch()
        if ord(ch) == 3:
            is_terminated = True
            return
        if ch.upper() == 'W':
            snake.change_dirct(0)
        if ch.upper() == 'S':
            snake.change_dirct(1)
        if ch.upper() == 'A':
            snake.change_dirct(2)
        if ch.upper() == 'D':
            snake.change_dirct(3)

snake = Snake()

t1 = threading.Thread(target = ctr, args=(snake, ))
t2 = threading.Thread(target = snake.run)

t1.start()
t2.start()


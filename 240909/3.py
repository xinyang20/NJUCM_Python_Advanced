from turtle import *

for steps in range(1, 500, 3):
    for c in ('red', 'orange', 'yellow', 'green', 'blue', 'purple'):
        color(c)
        forward(steps)
        right(30)

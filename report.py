import random, time

import profiteer

framerate = 30

profiteer.init(1, framerate)

while True:
    profiteer.reset()
    profiteer.report()
    profiteer.sample()
    time.sleep(1 / framerate)
    profiteer.advance()

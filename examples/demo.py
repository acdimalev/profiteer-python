import random, time

import profiteer

profiteer.init(2, 60)

for _ in range(60):
    profiteer.reset()
    pass
    profiteer.sample()
    time.sleep(0.001 * random.random())
    profiteer.sample()
    profiteer.advance()

profiteer.report()

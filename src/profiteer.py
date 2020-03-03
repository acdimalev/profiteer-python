"""
profiling for fun and profit

the rough idea is to quickly get an idea of how long some code takes to run in
the order of micro-seconds to milli-seconds.

start with a contrived example... .

>>> import random, time
>>> import profiteer
>>> profiteer.init(2, 10)
>>> for _ in range(10):
...     profiteer.reset()
...     pass
...     profiteer.sample()
...     time.sleep(0.001 * random.random())
...     profiteer.sample()
...     profiteer.advance()
...
>>> profiteer.report()

this will print a profile report with two histograms.

the first histogram shows how long nothing (`pass`) takes to run.
the second histogram shows how long a random sleep takes to run.

"""


import math, sys, time

import profiteer as self


# the total number of sample sets and iterations
# as set by `init`
SETS = 0
ITERATIONS = 0

# sample data
# allocated by `init`
# : list(bytearray)
samples = []

# the next set to sample into and current sampling iteration
set = 0
iteration = 0

# the last / reference timestamp (in microseconds)
last = 0


def init(sets, iterations):
    """allocate sample buffers"""
    self.SETS = sets
    self.ITERATIONS = iterations
    self.samples = [
        bytearray(iterations * [255])
        for _ in range(sets)
    ]
    self.set = 0
    self.iteration = 0


def reset():
    """reset the sample timer

    should be done at least once before collecting the first sample
    """
    self.last = _get_time_usec()


def sample():
    """record a sample

    records the time delta since the previous sample or reset.
    sets of samples are recorded in sampling order.
    """
    now = _get_time_usec()
    self.samples[self.set][self.iteration] = _logbin_time(now - self.last)
    self.set = (1 + self.set) % self.SETS
    self.last = _get_time_usec()


def advance():
    """advance to the next iteration of samples

    each iteration of samples always starts with the first sample set.

    i.e.

    >>> while True:
    ...     profiteer.reset()
    ...     profiteer.sample() # first sample set
    ...     profiteer.sample() # second sample set
    ...     profiteer.sample() # third sample set
    ...     profiteer.advance()
    ...
    """
    self.iteration = (1 + self.iteration) % self.ITERATIONS
    self.set = 0


def report():
    """print an ASCII-formatted report"""
    for samples in self.samples:
        buckets = [
            _logbin_population(samples.count(bucket))
            for bucket in range(22)
        ]
        piles = [
            buckets[:1],
            buckets[1:11],
            buckets[11:21],
            buckets[21:],
        ]
        f = lambda glyphs, buckets: "".join(glyphs[bucket] for bucket in buckets)
        print("|" + " ".join(f("   .:", pile) for pile in piles))
        print("|" + " ".join(f(" .:::", pile) for pile in piles))
        print("+" + " ".join(f("-----", pile) for pile in piles))

    print("       us         ms      ")


def _get_time_usec():
    return time.time_ns() // 1000


def _logbin_time(x):
    # one bucket, less than a microsecond
    # ten buckets, microseconds
    # ten buckets, milliseconds
    # one bucket, more than a second
    return min(21, int.bit_length(x))


def _logbin_population(x):
    return int.bit_length(math.ceil(0b1111 * x / self.ITERATIONS))


# compatibility
if sys.version_info[:2] < (3, 7):

    import math

    def _get_time_usec():
        return math.floor(time.time() * 1_000_000)

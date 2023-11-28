import time
from functools import partial
from threading import Thread, Lock
from queue import Queue
from typing import TYPE_CHECKING, Callable, Dict

import numpy as np

if TYPE_CHECKING:
    from bokeh_plot import BokehPlot


class Sensor(Thread):
    def __init__(self, plt: "BokehPlot", fns: Dict, delay_queue: Queue):
        Thread.__init__(self)

        self.ys = {}
        self.x = 0
        self.fns = fns
        self.delay_queue = delay_queue
        self.queueLock = Lock()

        self.sensor_callback = plt.update
        self.bokeh_callback = plt.doc.add_next_tick_callback

        self.i = 0


    def get_delay(self):
        with self.queueLock:
            delay = self.delay_queue.get()
            self.delay_queue.put(delay)

        return delay


    def run(self):
        while True:
            time.sleep(self.get_delay())

            self.data = {y: [fn(self.x)] for y, fn in self.fns.items()}
            self.data["x"] = [self.x]

            self.x += 0.35
            print( self.i)
            self.i +=1
            self.bokeh_callback(partial(self.sensor_callback, self.data))

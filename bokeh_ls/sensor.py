import time
from functools import partial
from threading import Thread
from typing import TYPE_CHECKING, Callable

import numpy as np

if TYPE_CHECKING:
    from bokeh_plot import BokehPlot


class Sensor(Thread):
    def __init__(self, plt: "BokehPlot", fn: Callable):
        Thread.__init__(self)
        self.vals = dict(x=0, y=0)
        self.fn = fn

        self.sensor_callback = plt.update
        self.bokeh_callback = plt.doc.add_next_tick_callback

    def run(self):
        while True:
            time.sleep(0.01)
            self.vals['x'] += 0.35
            self.vals['y'] = self.fn(self.vals['x'])

            self.bokeh_callback(partial(self.sensor_callback, self.vals))

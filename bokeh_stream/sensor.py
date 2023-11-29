import time
from collections import deque
from dataclasses import dataclass
from functools import partial
from threading import Lock, Thread, Event
from typing import TYPE_CHECKING, Callable, Dict
from datetime import datetime as dt
import numpy as np
from stack import RollingStack

if TYPE_CHECKING:
    from bokeh_plot import BokehPlot


@dataclass
class SensorDetails:
    fns: Dict[str, Callable]
    legend: Dict[str, str]
    title: str

    # a slight delay is needed for high frequency sensor data (>100Hz)
    delay_q: RollingStack
    data_q: RollingStack


class SensorProducer(Thread):
    def __init__(self, details: SensorDetails, sensor_is_reading: Event) -> None:
        Thread.__init__(self)
        self.details = details
        self.sensor_is_reading = sensor_is_reading
        self.fns = details.fns

        self.start_time = self.current_milli_time()
        self.x = self.start_time 

        self.data = {y: [0] for y, _ in details.fns.items()}
        self.data["x"] = [self.start_time]
        self.details.data_q.append(self.data)

    def run(self):
        while True:
            if self.sensor_is_reading.is_set():
                time.sleep(self.details.delay_q.latest())
                self.x = self.current_milli_time(self.start_time)/ 300
                self.data = {y: [fn(self.x)] for y, fn in self.fns.items()}
                self.data["x"] = [self.x]

                self.details.data_q.append(self.data)


    def read(self):
        return self.details.data_q.latest()
    
    def current_milli_time(self, start_time=0):
        return round(time.time() * 1000) - start_time


class SensorConsumer(Thread):
    def __init__(self, plt: "BokehPlot", sensor: SensorProducer, sensor_is_reading: Event):
        """Initialise pretend sensor data. This can be replaced with real data based on project

        Args:
            plt (BokehPlot): plot to display the data
            sensor (SensorProducer): class that supplies sensor data
        """
        Thread.__init__(self)

        self.sensor = sensor
        self.sensor_is_reading = sensor_is_reading
        self.threadLock = Lock()

        self.sensor_callback = plt.update
        self.bokeh_callback = plt.doc.add_next_tick_callback

    def run(self):
        """Generate data"""
        while True:
            time.sleep(self.sensor.details.delay_q.latest())

            if self.sensor_is_reading.is_set():
                with self.threadLock:
                    self.bokeh_callback(partial(self.sensor_callback, self.sensor.read()))

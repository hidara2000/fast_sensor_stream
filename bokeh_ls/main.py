from functools import partial
from itertools import cycle

import numpy as np
from bokeh_plot import BokehPage, BokehPlot, LayoutDefaults, PlotDefaults
from scipy import signal
from sensor import Sensor

c = lambda: cycle(
    [
        [np.cos, "Cos"],
        [np.sin, "Sin"],
        [signal.sawtooth, "Sawtooth"],
        [partial(signal.chirp, f0=6, f1=1, t1=10, method="linear"), "Chirp"],
        [partial(signal.sweep_poly, poly=np.poly1d([0.025, -0.36, 1.25, 2.0])), "Sweep"],
        [signal.square, "Square"],

    ]
)
my_iter = c()

def threads(plt: BokehPlot):
    global my_iter
    fn, _ = next(my_iter)
    sensor = Sensor(plt, fn)
    sensor.start()


def main():
    global my_iter
    plots = []

    main_page = BokehPage(LayoutDefaults())
    

    for _ in range(6):
        _, title = next(my_iter)
        plots.append(BokehPlot(main_page, sensor_thread=threads, defaults=PlotDefaults(plot_title=title)))

    # reset cycle so that titles match up
    my_iter = c()
    main_page.add_plots(plots)

    _ = [threads(x) for x in plots]


# Run command:
# bokeh serve --show bokeh_ls
main()

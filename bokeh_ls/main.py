from functools import partial
from itertools import cycle
from queue import Queue

import numpy as np
from bokeh_plot import BokehPage, BokehPlot, LayoutDefaults, PlotDefaults
from scipy.signal import chirp, sawtooth, square, sweep_poly
from sensor import Sensor

c = lambda: cycle(
    [
        {
            "fns": {"y": np.cos, "y1": np.sin},
            "ys_legend_text": {"y": "Cos(x)", "y1": "Sin(x)"},
            "title": "Cos & Sine Waves",
        },
        {
            "fns": {"y": np.sin},
            "ys_legend_text": {"y": "Sin(x)"},
            "title": "Simple Sin Wave",
        },
        {
            "fns": {"y": sawtooth},
            "ys_legend_text": {"y": "Sawtooth(x)"},
            "title": "Sawtooth",
        },
        {
            "fns": {"y": partial(chirp, f0=6, f1=1, t1=10, method="linear")},
            "ys_legend_text": {"y": "chirp(x)"},
            "title": "Chirp",
        },
        {
            "fns": {
                "y": partial(sweep_poly, poly=np.poly1d([0.025, -0.36, 1.25, 2.0]))
            },
            "ys_legend_text": {"y": "Sweep(x)"},
            "title": "Sweep",
        },
        {
            "fns": {"y": square},
            "ys_legend_text": {"y": "Square(x)"},
            "title": "Square",
        },
    ]
)
my_iter = c()
delay_queue = Queue()
delay_queue.put(0.01)


def threads(plt: BokehPlot):
    global my_iter, delay_queue

    my_signals = next(my_iter)
    sensor = Sensor(plt, my_signals["fns"], delay_queue)
    sensor.start()


def main():
    global my_iter, delay_queue

    plots = []

    main_page = BokehPage(LayoutDefaults(delay_queue=delay_queue))

    for _ in range(1):
        my_signals = next(my_iter)
        plots.append(
            BokehPlot(
                main_page,
                sensor_thread=threads,
                defaults=PlotDefaults(
                    plot_title=my_signals["title"],
                    ys_legend_text=my_signals["ys_legend_text"],
                ),
            )
        )

    # reset cycle so that titles match up
    my_iter = c()
    main_page.add_plots(plots)

    _ = [threads(x) for x in plots]


# Run command:
# bokeh serve --show bokeh_ls
main()

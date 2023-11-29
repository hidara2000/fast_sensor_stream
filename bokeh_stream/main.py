from functools import partial
from itertools import cycle
from threading import Event

import numpy as np
from bokeh_plot import BokehPage, BokehPlot, LayoutDefaults, PlotDefaults
from scipy.signal import chirp, sawtooth, square, sweep_poly
from sensor import RollingStack, SensorConsumer, SensorDetails, SensorProducer


def gen_fake_data(delay_queue):
    return cycle(
        [
            SensorDetails(
                {"y": np.cos, "y1": np.sin},
                {"y": "Cos(x)", "y1": "Sin(x)"},
                "Cos & Sine Waves",
                delay_queue,
                RollingStack(3),
            ),
            SensorDetails(
                {"y": np.sin},
                {"y": "Sin(x)"},
                "Simple Sin Wave",
                delay_queue,
                RollingStack(3),
            ),
            SensorDetails(
                {"y": sawtooth},
                {"y": "Sawtooth(x)"},
                "Sawtooth",
                delay_queue,
                RollingStack(3),
            ),
            SensorDetails(
                {"y": partial(chirp, f0=6, f1=1, t1=10, method="linear")},
                {"y": "chirp(x)"},
                "Chirp",
                delay_queue,
                RollingStack(3),
            ),
            SensorDetails(
                {"y": partial(sweep_poly, poly=np.poly1d([0.025, -0.36, 1.25, 2.0]))},
                {"y": "Sweep(x)"},
                "Sweep",
                delay_queue,
                RollingStack(3),
            ),
            SensorDetails(
                {"y": square},
                {"y": "Square Wave(x)"},
                "Square",
                delay_queue,
                RollingStack(3),
            ),
        ]
    )


def main():
    """Create live plots"""
    n_plots = 6
    sensor_speed_slider_value = 0.0025 * n_plots

    delay_queue = RollingStack(1, sensor_speed_slider_value)
    iter_fake_sensors = gen_fake_data(delay_queue)
    sensor_is_reading = Event()
    sensor_is_reading.set()

    plots = []

    main_page = BokehPage(
        LayoutDefaults(
            delay_queue, sensor_speed_slider_value=sensor_speed_slider_value
        ),
        sensor_is_reading,
    )

    for _ in range(n_plots):
        my_signal = next(iter_fake_sensors)

        producer = SensorProducer(my_signal, sensor_is_reading)
        plt = BokehPlot(main_page, my_signal)
        consumer = SensorConsumer(plt, producer, sensor_is_reading)

        plots.append(plt)
        producer.start()
        consumer.start()

    main_page.add_plots(plots)


# Run command:
# bokeh serve --show bokeh_ls
main()

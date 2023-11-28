from dataclasses import asdict, dataclass, field
from pprint import pformat
from typing import List

from bokeh.io import curdoc
from bokeh.layouts import column, gridplot
from bokeh.models import ColumnDataSource, HoverTool, Legend
from bokeh.models.widgets import CheckboxGroup, Div, Slider
from bokeh.plotting import figure
from sensor import Sensor
from tornado import gen


@dataclass
class GenericDataclass:
    def __str__(self) -> str:
        return pformat(self.dict(), indent=4)

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class PlotDefaults(GenericDataclass):
    plot_tools: str = "box_zoom,pan,wheel_zoom,reset"
    tooltips: List = field(
        default_factory=lambda: [
            ("index", "$index"),
            (
                "(x,y)",
                "(@x, $y)",
            ),
        ]
    )

    # plot data
    plot_title: str = "Sensor Data"
    xaxis_label: str = "TS"
    yaxis_label: str = "Value"
    plot_width: int = 1000
    plot_height: int = 500


@dataclass
class LayoutDefaults(GenericDataclass):
    page_title: str = "Real Time Sensor Data"
    page_title_colour: str = "white"
    page_title_width: int = 1000
    page_title_height: int = 75

    # how much data to scroll
    slider_start: int = 1
    slider_end: int = 200
    slider_value: int = 30
    slider_step: int = 1


class BokehPage:
    def __init__(self, defaults: LayoutDefaults) -> None:
        self.doc = curdoc()
        curdoc().theme = "dark_minimal"

        self.defaults = defaults
        self.window_width = self.defaults.slider_value
        self.start_stop_checkbox = None
        self.window_width_slider = None
        self.all_plots = None
        self.plots = None

        self.header = Div(
            text=f"<h1 style='color:{defaults.page_title_colour}'>{defaults.page_title}</h1>",
            width=defaults.page_title_width,
            height=defaults.page_title_height,
            background="black",
        )

    def add_plots(self, plots: List["BokehPlot"]):
        self.plots = plots
        gplot = []

        for p in plots:
            gplot.append(p.plt)
            # gplot.append([None])

        n = 2
        gplot = [gplot[i : i + n] for i in range(0, len(gplot), n)]
        self.all_plots = gridplot(
            gplot,
        )
        self.all_plots.spacing = 10
        self.layout()

    def layout(self):
        self.doc.title = self.defaults.page_title

        self.start_stop_checkbox = CheckboxGroup(
            labels=["Enable Plotting"], active=[0]
        )
        self.start_stop_checkbox.on_change("active", self.start_stop_handler)

        self.window_width_slider = Slider(
            start=self.defaults.slider_start,
            end=self.defaults.slider_end,
            value=self.defaults.slider_value,
            step=self.defaults.slider_step,
            title="window_width",
        )
        self.window_width_slider.on_change("value", self.window_width_handler)

        itms = [
            self.header,
            self.start_stop_checkbox,
            self.window_width_slider,
            self.all_plots,
        ]
        for itm in itms:
            itm.sizing_mode = "stretch_width"

        layout = column(*itms)
        layout.sizing_mode = "stretch_width"

        self.doc.add_root(layout)

    def start_stop_handler(self, attr, old, new):
        for p in self.plots:
            if 0 in list(new):
                p.is_plotting = True
            else:
                p.is_plotting = False

    def window_width_handler(self, attr, old, new):
        self.window_width = new


class BokehPlot:
    def __init__(
        self, parent: BokehPage, sensor_thread: Sensor, defaults: PlotDefaults
    ) -> None:
        self.parent = parent
        self.doc = parent.doc

        self.is_plotting = True

        self.sensor_thread = sensor_thread
        self.defaults = defaults

        self.plot_options = dict(
            width=defaults.plot_width,
            height=defaults.plot_height,
            tools=[HoverTool(tooltips=defaults.tooltips), defaults.plot_tools],
        )

        self.source, self.plt = self.definePlot()

    def definePlot(self):
        plt = figure(**self.plot_options, title=self.defaults.plot_title)
        plt.sizing_mode = "scale_width"
        plt.xaxis.axis_label = self.defaults.xaxis_label
        plt.yaxis.axis_label = self.defaults.yaxis_label

        source = ColumnDataSource(data=dict(x=[0], y=[0]))

        r1 = plt.line(x="x", y="y", source=source, line_width=2)
        r1a = plt.circle(x="x", y="y", source=source, fill_color="white", size=5)

        legend = Legend(items=[(self.defaults.plot_title, [r1, r1a])])
        plt.add_layout(legend, "right")
        plt.legend.click_policy = "hide"

        return source, plt

    @gen.coroutine
    def update(self, new_data):
        if self.is_plotting:
            new_data = {k:[v] for k,v in new_data.items()}
            self.source.stream(new_data, rollover=self.parent.window_width)

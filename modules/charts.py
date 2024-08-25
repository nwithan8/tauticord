import logging
from collections.abc import Callable
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from modules.utils import seconds_to_hours_minutes

MIN_TEXT_BOTTOM_PADDING = 0

PLAY_COUNT_FORMATTER = plt.FuncFormatter(lambda x, _: f'{int(x)}')
PLAY_DURATION_FORMATTER = plt.FuncFormatter(lambda x, _: seconds_to_hours_minutes(x))


class ChartMaker:
    def __init__(self,
                 x_axis: list,
                 x_axis_labels: list[str],
                 title: str = None,
                 x_axis_name: str = None,
                 y_axis_name: str = None,
                 x_axis_major_formatter=None,
                 x_axis_minor_formatter=None,
                 y_axis_major_formatter=None,
                 y_axis_minor_formatter=None,
                 y_axis_tick_calculator=None,
                 text_color: str = None,
                 background_color: str = None,
                 grid_line_color: str = None):
        self._title: str = title
        self._x_axis: list = x_axis
        self._x_axis_labels: list[str] = x_axis_labels
        self._x_axis_name: str = x_axis_name
        self._y_axis_name: str = y_axis_name
        self._x_axis_major_formatter = x_axis_major_formatter
        self._x_axis_minor_formatter = x_axis_minor_formatter
        self._y_axis_major_formatter = y_axis_major_formatter
        self._y_axis_minor_formatter = y_axis_minor_formatter
        self._y_axis_tick_calculator = y_axis_tick_calculator
        self._text_color: str = text_color
        self._enable_grid_lines: bool = grid_line_color is not None

        # Set up initial figure and single plot
        # TODO: Set minimum dimensions for plot
        self._figure: Figure = plt.figure()
        self._plot: Axes = self._figure.add_subplot(1, 1, 1)
        if background_color:
            self._figure.set_facecolor(background_color)
            self._plot.set_facecolor(background_color)
        if self._enable_grid_lines:
            self._plot.yaxis.grid(True, color=grid_line_color, linestyle='-', linewidth=0.5,
                                  zorder=0)  # zorder=0 to draw first (behind data lines)
            self._plot.tick_params(colors=background_color or None, which='both')

    def save(self, path: str):
        # Delay text formatting until after plot is created and data/markers added

        # Hide border/outline around plot
        spines = ['top', 'bottom', 'left', 'right']
        for spine in spines:
            self._plot.spines[spine].set_visible(False)

        # Set axis labels and title
        text_params = {
            'fontweight': 'bold',
            'color': self._text_color
        }
        if self._x_axis_name:
            self._plot.set_xlabel(self._x_axis_name, **text_params)
        if self._y_axis_name:
            self._plot.set_ylabel(self._y_axis_name, **text_params)
        if self._title:
            self._plot.set_title(self._title, **text_params)

        # Set axis ticks and labels
        self._plot.set_xticks(self._x_axis)
        self._plot.set_xticklabels(self._x_axis_labels, rotation=45, ha='right', color=self._text_color)
        y_axis_tick_labels = self._plot.get_yticklabels()
        self._plot.set_yticklabels(y_axis_tick_labels, color=self._text_color)
        if self._y_axis_tick_calculator:
            y_min_value, y_max_value = self._plot.get_ylim()
            ticks = self._y_axis_tick_calculator(y_min_value, y_max_value)
            self._plot.yaxis.set_ticks(ticks)

        # Set formatters and locators for axes
        if self._x_axis_major_formatter:
            self._plot.xaxis.set_major_formatter(self._x_axis_major_formatter)
        if self._x_axis_minor_formatter:
            self._plot.xaxis.set_minor_formatter(self._x_axis_minor_formatter)
        if self._y_axis_major_formatter:
            self._plot.yaxis.set_major_formatter(self._y_axis_major_formatter)
        if self._y_axis_minor_formatter:
            self._plot.yaxis.set_minor_formatter(self._y_axis_minor_formatter)

        # Add legend
        self._plot.legend()

        # Set tight layout
        self._figure.set_tight_layout(3)

        # Write the chart to a file
        plt.savefig(path)
        logging.info(f"Saved chart to {path}")

    def add_line(self, values: list, label: str = None, marker: str = None, line_style: str = None,
                 line_color: str = None, text_color: str = None, value_text_formatter: Callable[[Any], str] = None):
        self._plot.set_axisbelow(True)
        kwargs = {}
        if label:
            kwargs['label'] = label
        if marker:
            kwargs['marker'] = marker
        if line_style:
            kwargs['linestyle'] = line_style
        if line_color:
            kwargs['color'] = line_color
            kwargs['markerfacecolor'] = line_color
            kwargs['markeredgecolor'] = line_color

        if not value_text_formatter:
            def value_text_formatter_function(x: Any) -> str:
                return f'{x}'

            value_text_formatter = value_text_formatter_function

        self._plot.plot(self._x_axis, values, **kwargs)

        # Add value text to each point
        for i, value in enumerate(values):
            if value == 0:
                continue
            self._plot.text(self._x_axis[i], value + 1, value_text_formatter(value), ha='center',
                            va='bottom', fontsize=8,
                            color=text_color or self._text_color)

    def add_stacked_bar(self, values: list[list], labels: list[str], bar_width: float = 0.8,
                        bar_colors: list[str] = None, text_color: str = None,
                        value_text_formatter: Callable[[Any], str] = None):
        self._plot.set_axisbelow(True)
        bottom = [0] * len(self._x_axis)

        if not value_text_formatter:
            def value_text_formatter_function(x: Any) -> str:
                return f'{x}'

            value_text_formatter = value_text_formatter_function

        for i, value in enumerate(values):
            kwargs = {}
            if bar_colors:
                kwargs['color'] = bar_colors[i]
            self._plot.bar(self._x_axis, value, width=bar_width, label=labels[i], bottom=bottom, **kwargs)
            bottom = [sum(x) for x in zip(bottom, value)]
            # Add value text to each bar
            for j, sub_value in enumerate(value):
                if sub_value == 0:
                    continue
                self._plot.text(self._x_axis[j], max(bottom[j] - 1.5, MIN_TEXT_BOTTOM_PADDING),
                                value_text_formatter(sub_value),
                                ha='center', va='bottom', fontsize=8,
                                color=text_color or self._text_color)

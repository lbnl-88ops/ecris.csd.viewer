from dataclasses import dataclass
from logging import info
import tkinter as tk
from matplotlib.figure import Figure
from typing import Dict
from itertools import compress
from collections import deque

from matplotlib.markers import MarkerStyle
from matplotlib.text import Text

from ops.ecris.analysis.model import Element


@dataclass
class _Label:
    artist: Text
    draw: bool = False


class ElementIndicator:
    MARKERS = deque(["v", "^", "p", "d", "*", "D"])

    def __init__(
        self,
        element: Element,
        is_plotted: tk.BooleanVar,
    ):
        self.marker_artist = None
        # self.marker_artist.set_visible(False)
        # self.label_artists = [_Label(a) for a in label_artists]
        self.element = element
        self._is_plotted = is_plotted
        self._is_plotted.trace_add("write", self._set_label)
        q_values = range(1, element.atomic_number + 1)
        self._m_over_q_values = [element.atomic_mass / q for q in q_values]
        # self.element_artist = element_artist
        self._marker = None
        self._label_artists: Dict[float, Artist] = {}
        self.color = None

    def is_visible(self, x_limits):
        x_min, x_max = x_limits
        return any(x_min <= x <= x_max for x in self._m_over_q_values)

    @property
    def is_plotted(self) -> bool:
        return self._is_plotted.get()

    @is_plotted.setter
    def is_plotted(self, to_set) -> None:
        self._is_plotted.set(to_set)

    def _get_element_y_value(self, figure: Figure, y_value, y_limits):
        y_min, y_max = y_limits
        new_system_loc = figure.gca().transData.transform((0, y_value))
        return figure.gca().transAxes.inverted().transform(new_system_loc)[1]

    def _get_label_y_value(self, y_value, y_limits):
        y_min, y_max = y_limits
        offset = 0.02 * abs(y_max - y_min)
        return y_value + offset

    def _remove_artists(self):
        if self.marker_artist is not None:
            self.marker_artist.remove()
            self.marker_artist = None
        if self._label_artists:
            for label in self._label_artists.values():
                label.remove()
            self._label_artists = {}

    def _set_label(self, *args, **kwargs):
        if self.marker_artist is not None:
            self.marker_artist.set_label(f"_{self.element.name}")
            info(f"is_plotted: {self._is_plotted.get()}")
            self._remove_artists()

    def _draw_labels(self, figure: Figure, plot_lines: bool):
        ax = figure.gca()
        ax_min, ax_max = ax.get_xlim()
        x_min = ax.transData.transform((ax_min, 0))[0]
        x_max = ax.transData.transform((ax_max, 0))[0]
        space_required = 35
        visible_labels = sorted(
            [
                l
                for l in self._label_artists.values()
                if x_min < ax.transData.transform(l.get_position())[0] < x_max
            ],
            key=lambda l: l.get_position()[0],
        )
        if not visible_labels:
            return
        label_x_positions = [
            ax.transData.transform(l.get_position())[0] for l in visible_labels
        ]
        visible = []
        last_visible = None
        for x_position in label_x_positions:
            if last_visible is None:
                visible.append(True)
                last_visible = x_position
                continue
            if abs(x_position - last_visible) > space_required:
                visible.append(True)
                last_visible = x_position
            else:
                visible.append(False)
        for is_visible, label in zip(visible, visible_labels):
            if is_visible:
                figure.draw_artist(label)
                if plot_lines:
                    x = label.get_position()[0]
                    line = ax.axvline(
                        x,
                        ls="--",
                        alpha=0.25,
                        c=self.marker_artist.get_color(),
                        animated=True,
                    )
                    figure.draw_artist(line)

    def draw(self, figure: Figure, y_value: float, lines=False) -> None:
        ax = figure.gca()
        max_mq = ax.get_xlim()[1]
        mask = [mq < max_mq for mq in self._m_over_q_values]
        m_over_q = list(compress(self._m_over_q_values, mask))
        q_values = list(compress(range(1, self.element.atomic_number + 1), mask))
        if self._marker is None:
            self._marker = MarkerStyle(ElementIndicator.MARKERS[0])
            ElementIndicator.MARKERS.rotate()
        if self.color is not None:
            (self.marker_artist,) = ax.plot(
                m_over_q,
                [y_value] * len(m_over_q),
                marker=self._marker,
                ms=10,
                ls="",
                markeredgecolor="black",
                animated=True,
                color=self.color,
            )
        else:
            (self.marker_artist,) = ax.plot(
                m_over_q,
                [y_value] * len(m_over_q),
                marker=self._marker,
                ms=10,
                ls="",
                markeredgecolor="black",
                animated=True,
            )
            self.color = self.marker_artist.get_color()
        for x, q in zip(m_over_q, q_values):
            txt = ax.text(
                x,
                self._get_label_y_value(y_value, ax.get_ylim()),
                f"{q}",
                animated=True,
                c="black",
                ha="center",
                va="bottom",
                weight="bold",
                clip_on=True,
            )
            self._label_artists[q] = txt
        self.element_artist = ax.text(
            1.01,
            self._get_element_y_value(figure, y_value, ax.get_ylim()),
            f"{self.element.symbol}-{round(self.element.atomic_mass)}",
            transform=ax.transAxes,
            weight="bold",
            animated=True,
            color=self.color,
        )

        figure.draw_artist(self.marker_artist)
        figure.draw_artist(self.element_artist)
        self._draw_labels(figure, lines)
        info(
            f"Element indicator for: {self.element.symbol}-{self.element.atomic_number}: label_artists: {len(self._label_artists)}"
        )


def add_element_indicators(elements: Dict[Element, tk.BooleanVar]):
    element_indicators = []
    for element, visibility in elements.items():
        element_indicators.append(ElementIndicator(element, visibility))
    return element_indicators

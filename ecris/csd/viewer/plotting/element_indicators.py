import tkinter as tk
from matplotlib import transforms
from matplotlib.figure import Figure
from typing import List, Dict
from itertools import compress

from matplotlib.markers import MarkerStyle

from ecris.csd.viewer.analysis import Element

class ElementIndicator:
    def __init__(self, marker_artist, label_artists, element: Element,
                 is_plotted: tk.BooleanVar,
                 element_artist):
        self.marker_artist = marker_artist
        self.label_artists = label_artists
        self.element = element
        self._is_plotted = is_plotted
        self._is_plotted.trace_add('write', self._set_label)
        self.is_plotted = False
        self.element_artist = element_artist

    def draw(self, figure: Figure, lines = False) -> None:
        figure.draw_artist(self.marker_artist)
        figure.draw_artist(self.element_artist)
        for label in self.label_artists:
            figure.draw_artist(label)
        if lines:
            ax = figure.gca()
            for x in self.marker_artist.get_xdata():
                line = ax.axvline(x, ls='--', alpha=0.25, c=self.marker_artist.get_color(), animated=True)
                figure.draw_artist(line)

    @property
    def is_plotted(self) -> bool:
        return self._is_plotted.get()

    def _set_label(self, *args, **kwargs):
        self.marker_artist.set_label(f'_{self.element.name}')
        # if self._is_plotted.get():
            # self.marker_artist.set_label(f"{self.element.symbol}-{self.element.atomic_weight}")
        # else:
            # self.marker_artist.set_label(f'_{self.element.name}')
    
    @is_plotted.setter
    def is_plotted(self, to_set) -> None:
        self._is_plotted.set(to_set)

    def set_x_scale(self, figure):
        ax = figure.gca()
        ax_min, ax_max = ax.get_xlim()
        x_min = ax.transData.transform((ax_min, 0))[0]
        x_max = ax.transData.transform((ax_max, 0))[0]
        space_required = 0.03*(x_max - x_min)
        visible_labels = sorted([l for l in self.label_artists if x_min < ax.transData.transform(l.get_position())[0] < x_max],
                                key=lambda l: l.get_position()[0])
        if not visible_labels:
            return
        label_x_positions = [ax.transData.transform(l.get_position())[0] for l in visible_labels]
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
        for v, l in zip(visible, visible_labels):
            l.set_alpha(1 if v else 0)

    def set_y_value(self, figure, y_value, y_limits):
        y_min, y_max = y_limits
        self.marker_artist.set_ydata([y_value]*len(self.marker_artist.get_xdata()))
        new_system_loc = figure.gca().transData.transform((0, y_value))
        new_axes_loc = figure.gca().transAxes.inverted().transform(new_system_loc)
        self.element_artist.set_y(new_axes_loc[1])
        offset = 0.02*abs(y_max - y_min)
        for label in self.label_artists:
            label.set_y(y_value + offset)

    def is_visible(self, x_limits):
        x_min, x_max = x_limits
        return any(x_min <= x <= x_max for x in self.marker_artist.get_xdata())

def add_element_indicators(elements: Dict[Element, tk.BooleanVar], figure: Figure):
    markers = ["v", "^", "p", "d", "*", "D"]
    element_indicators = []
    ax = figure.gca()
    for element, visibility in elements.items():
        labels = []
        q_values = range(1, element.atomic_number + 1)
        m_over_q = [element.atomic_weight/q for q in q_values]
        mask = [mq < 10 for mq in m_over_q]
        q_values = list(compress(q_values, mask))
        m_over_q = list(compress(m_over_q, mask))
        height = 0
        marker = MarkerStyle(markers.pop(0))
        ln, = ax.plot(m_over_q, [height]*len(m_over_q), 
                marker=marker,
                ms=10,
                ls='',
                markeredgecolor='black',
                # label=element.name,
                animated=True)
        for x, q in zip(m_over_q, q_values):
            txt = ax.text(x, height, f"{q}", animated=True, c='black',
                          ha='center', va='bottom',
                          weight='bold', clip_on = True)
            labels.append(txt)
        element_artist = ax.text(1.01, 0, f"{element.symbol}-{element.atomic_weight}", 
                                 transform=ax.transAxes, weight='bold', animated=True,
                                 color=ln.get_color())
        element_indicators.append(ElementIndicator(ln, labels, element, visibility, element_artist))
    return element_indicators





    
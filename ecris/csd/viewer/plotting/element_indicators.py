from dataclasses import dataclass
from matplotlib.figure import Figure
from typing import List

from matplotlib.markers import MarkerStyle

@dataclass
class Element:
    name: str
    atomic_weight: int
    atomic_number: int

PERSISTANT_ELEMENTS = [
    Element(name, weight, number)
    for name, weight, number in zip(["C", "N", "O"],
                                    [12,  14,  16],
                                    [ 6,   7,   8])    
]

VARIABLE_ELEMENTS = [
    Element(name, weight, number) 
    for name, weight, number in zip(["V"],
                                    [51],
                                    [23])
]

class ElementIndicator:
    def __init__(self, marker_artist, label_artists):
        self.marker_artist = marker_artist
        self.label_artists = label_artists

    def set_x_scale(self, figure):
        ax = figure.gca()
        ax_min, ax_max = ax.get_xlim()
        x_min = ax.transData.transform((ax_min, 0))[0]
        x_max = ax.transData.transform((ax_max, 0))[0]
        print(x_min, x_max)
        space_required = 0.1*(x_max - x_min)
        visible_labels = sorted([l for l in self.label_artists if x_min < ax.transData.transform(l.get_position())[0] < x_max],
                                key=lambda l: l.get_position()[0])
        print(visible_labels)
        if not visible_labels:
            return
        label_x_positions = [ax.transData.transform(l.get_position())[0] for l in visible_labels]
        visible = []
        last_visible = None
        for x_position in label_x_positions:
            if last_visible is None:
                print(f'No last visible, setting to {x_position}')
                visible.append(True)
                last_visible = x_position
                continue
            if abs(x_position - last_visible) > space_required:
                print(f'Value {x_position} - {last_visible} > {space_required}, showing')
                visible.append(True)
                last_visible = x_position
            else:
                print(f'Value {x_position} - {last_visible} < {space_required}, hiding')
                visible.append(False)
        for v, l in zip(visible, visible_labels):
            l.set_alpha(1 if v else 0)

    def set_y_limits(self, y_limits, scale):
        y_min, y_max = y_limits
        height = (y_max + y_min)/2 * scale
        self.marker_artist.set_ydata([height]*len(self.marker_artist.get_xdata()))
        offset = 0.02*abs(y_max - y_min)
        for label in self.label_artists:
            label.set_y(height + offset)

    def is_visible(self, x_limits):
        x_min, x_max = x_limits
        return any(x_min < x < x_max for x in self.marker_artist.get_xdata())

def add_element_indicators(elements: List[Element], figure: Figure):
    markers = ["v", "^", "p", "d", "*", "D"]
    element_indicators = []
    ax = figure.gca()
    for i, element in enumerate(elements):
        labels = []
        m_over_q = [element.atomic_weight/n for n in range(1, element.atomic_number)]
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        height = (i + 1)*(y_max + y_min)/len(elements)/2
        to_plot = [m for m in m_over_q if x_min <= m <= x_max]
        marker = MarkerStyle(markers[i % len(markers)])
        ln, = ax.plot(to_plot, [height]*len(to_plot), 
                marker=marker,
                ms=10,
                ls='',
                label=element.name,
                animated=True)
        offset = 0.1*abs(y_max - y_min)
        for x in to_plot:
            txt = ax.text(x, height + offset, f"{x:.1f}", animated=True, c=ln.get_color(),
                          ha='center', va='bottom',
                          weight='bold', clip_on = True)
            labels.append(txt)
        element_indicators.append(ElementIndicator(ln, labels))
    ax.legend()
    return element_indicators




    
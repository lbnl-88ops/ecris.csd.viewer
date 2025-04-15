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

    def is_visible(self, x_limits):
        x_min, x_max = x_limits
        return any(x_min < x < x_max for x in self.marker_artist.get_xdata())

def add_element_indicators(elements: List[Element], figure: Figure):
    markers = ["v", "^", "p", "d", "*", "D"]
    element_indicators = []
    for i, element in enumerate(elements):
        labels = []
        m_over_q = [element.atomic_weight/n for n in range(1, element.atomic_number)]
        ax = figure.gca()
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
        for x in to_plot:
            offset = marker.get_path().transformed(marker.get_transform()).get_extents().height
            txt = ax.text(x, height + offset, f"{x:.1f}", animated=True, c=ln.get_color(),
                          ha='center', va='bottom',
                          weight='bold')
            labels.append(txt)
        element_indicators.append(ElementIndicator(ln, labels))
    return element_indicators




    
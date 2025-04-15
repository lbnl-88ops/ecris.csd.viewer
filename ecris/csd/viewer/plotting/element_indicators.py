from dataclasses import dataclass
from matplotlib.figure import Figure
from typing import List

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

def add_element_indicators(elements: List[Element], figure: Figure):
    markers = ["v", "^", "p", "d", "*", "D"]
    artists = []
    for i, element in enumerate(elements):
        m_over_q = [element.atomic_weight/n for n in range(1, element.atomic_number)]
        ax = figure.gca()
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        height = (i + 1)*(y_max + y_min)/len(elements)/2
        to_plot = [m for m in m_over_q if x_min <= m <= x_max]
        ln, = ax.plot(to_plot, [height]*len(to_plot), 
                marker=markers[i % len(markers)],
                ms=10,
                ls='',
                label=element.name,
                animated=True)
        artists.append(ln)
    return artists




    
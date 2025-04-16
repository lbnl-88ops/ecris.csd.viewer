from dataclasses import dataclass

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
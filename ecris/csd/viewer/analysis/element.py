from dataclasses import dataclass

@dataclass(eq=True, frozen=True)
class Element:
    name: str
    symbol: str
    atomic_weight: int
    atomic_number: int

PERSISTANT_ELEMENTS = [
    Element(name, symbol, weight, number)
    for name, symbol, weight, number in zip(["Carbon", "Nitrogen", "Oxygen"],
                                    ["C", "N", "O"],
                                    [12,  14,  16],
                                    [ 6,   7,   8])    
]

VARIABLE_ELEMENTS = [
    Element(name, symbol, weight, number) 
    for name, symbol, weight, number in zip(["Vanadium"], ["V"],
                                    [51],
                                    [23])
]
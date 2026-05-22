from dataclasses import dataclass

@dataclass
class Atom:
    Z: int
    symbol: str
    weight: float

ATOM_DATA = {      # add more elements here as needed
    1: Atom(1, "H", 1.00782503),
    2: Atom(2, "He", 4.00260325),
    3: Atom(3, "Li", 7.01600344),
    4: Atom(4, "Be", 9.01218307),
    5: Atom(5, "B", 11.00930536),
    6: Atom(6, "C", 12.00000000),
    7: Atom(7, "N", 14.00307400),
    8: Atom(8, "O", 15.99491462),
    9: Atom(9, "F", 18.99840316),
    10: Atom(10, "Ne", 19.99244018),
    11: Atom(11, "Na", 22.98976928),
    12: Atom(12, "Mg", 23.98504170),
    13: Atom(13, "Al", 26.98153853),
    14: Atom(14, "Si", 27.97692653),
    15: Atom(15, "P", 30.97376199),
    16: Atom(16, "S", 31.97207117),
    17: Atom(17, "Cl", 34.96885268),
    18: Atom(18, "Ar", 39.96238312),
    19: Atom(19, "K", 38.96370649),
    20: Atom(20, "Ca", 39.96259086),
}

#to extract Atom(Z, "symbol", weight)
symbol_to_atom = {
    atom.symbol: atom for atom in ATOM_DATA.values()
}


#print(symbol_to_atom["Ca"].Z)  #to check
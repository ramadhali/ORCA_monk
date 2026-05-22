from dataclasses import dataclass
from pathlib import Path
from orca_io.periodic_table import ATOM_DATA, symbol_to_atom, Atom

@dataclass
class AtomCoordinate:
    atom: Atom
    x: float
    y: float
    z: float

# to read atom info, atom.Z and atom.symbol both are considered
def get_atom_from_xyz_token(token):
    """XYZ may contain:
    C / H/ Ca
    or
    6 / 1 / 20
    """

    if token.isdigit():
        return ATOM_DATA[int(token)]
    
    # if not atomic number, convert ca/ar to Ca/Ar
    return symbol_to_atom[token.capitalize()]
    
def read_xyz(xyz_file):
    lines=Path(xyz_file).read_text().splitlines()

    natoms  = int(lines[0])
    comment = lines[1]
    atom_lines = lines[2:2 + natoms]

    atoms = []

    for line in atom_lines:
        parts = line.split()
        
        atom=get_atom_from_xyz_token(parts[0])

        atoms.append(
            AtomCoordinate(
                atom=atom,
                x=float(parts[1]),
                y=float(parts[2]),
                z=float(parts[3]),
            )
        )
    
    return {
        "natoms": natoms,
        "comment": comment,
        "atoms": atoms
    }
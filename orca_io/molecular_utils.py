from pathlib import Path
from orca_io.xyz_parser import AtomCoordinate, get_atom_from_xyz_token, read_xyz

def molecular_weight(xyz_data):
    return sum(atom_coord.atom.weight for atom_coord in xyz_data["atoms"]
    )

def electron_count(xyz_data,charge=0):
    return sum(atom_coord.atom.Z for atom_coord in xyz_data["atoms"]) - charge

def guess_multiplicity(xyz_data,charge=0):
    total_electrons=electron_count(xyz_data,charge)

    if total_electrons % 2 == 0:
        return 1
    return 2


# to test if this is working
""" 
xyz_data=read_xyz("input_xyz/test.xyz")
print(molecular_weight(xyz_data))
print(electron_count(xyz_data,charge=0))
print(guess_multiplicity(xyz_data,charge=-3))
"""
import re

# parser for ground state: scf, freq, themo, homo/lumo

# Extract SCF energy and status for ORCA job
def parse_scf_properties(output_text):
    energy_matches=re.findall(
        r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)",
        output_text
    )

    energy=float(energy_matches[-1]) if energy_matches else None
    normal_termination="ORCA TERMINATED NORMALLY" in output_text

    homo,lumo,gap=parse_homo_lumo(output_text)
    return{
        "final_energy_hartree":energy,
        "normal_termination":normal_termination,
        "HOMO_eV":homo,
        "LUMO_eV":lumo,
        "gap_eV":gap,
    }

# Extract HOMO, LUMO, Gap for Orca job
def parse_homo_lumo(output_text):
    lines=output_text.splitlines()
    orbital_energies=[]
    reading=False

    for line in lines:
        if "NO" in line and "OCC" in line and "E(eV)" in line:
            # dont reset orbital_energies, it will erase SPIN(up) in that case
            reading=True
            continue

        if reading and (not line.strip() or "*Only the first" in line):
            reading=False
            continue

        if reading:
            parts=line.split()
            if len(parts)>=4:
                try:
                    occ=float(parts[1])
                    energy_eV=float(parts[3])
                    orbital_energies.append((occ,energy_eV))
                except ValueError:
                    pass

    # Separate based on occupancy
    occupied=[e_h for occ,e_h in orbital_energies if occ > 0.0]
    virtual=[e_h for occ,e_h in orbital_energies if occ == 0.0]

    if occupied:
        occupied.sort()
        homo=occupied[-1]
    else:
        homo=None

    if virtual:
        virtual.sort()
        lumo=virtual[0]
    else:
        lumo=None

    gap=lumo-homo if homo is not None and lumo is not None else None

    return homo,lumo,gap

# Extract Optimization convergence
def parse_optimization_properties(output_text):
    optimization_converged="THE OPTIMIZATION HAS CONVERGED" in output_text
    optimization_cycles=len(re.findall(r"GEOMETRY OPTIMIZATION CYCLE\s+\d+", output_text))

    return {
        "optimization_converged": optimization_converged,
        "optimization_cycles": optimization_cycles
    }

# ORCA Freq parsing
def parse_frequency_properties(output_text): # Now works if only one frew block
    frequencies=re.findall(
        r"(-?\d+\.\d+)\s+cm\*\*-1",
        output_text
    )

    frequencies=[float(freq) for freq in frequencies]

    imaginary_frequencies=[freq for freq in frequencies if freq < 0.0]
    all_frequencies=[freq for freq in frequencies if abs(freq) > 1.0]

    return{
        "n_frequencies": len(frequencies),
        "n_imaginary_frequencies": len(imaginary_frequencies),
        "lowest_frequency_cm-1": min(all_frequencies) if all_frequencies else None
    }


# for ZPE/Enthalpy/Gibbs
def parse_thermochemistry_properties(output_text):
    patterns={
        "zero_point_energy_hartree": r"Zero point energy\s+\.\.\.\s+(-?\d+\.\d+)\s+Eh",
        "enthalpy_hartree": r"Total Enthalpy\s+\.\.\.\s+(-?\d+\.\d+)\s+Eh",
        "gibbs_free_energy_hartree": r"Final Gibbs free energy\s+\.\.\.\s+(-?\d+\.\d+)\s+Eh",
    }
    thermo_properties={
        "zero_point_energy_hartree": None,
        "enthalpy_hartree": None,
        "gibbs_free_energy_hartree": None
    }

    # we will do reverse search, so the loop close just after the first macth at bottom
    lines=output_text.splitlines()

    for line in reversed(lines):
        for key,pattern in patterns.items():
            if thermo_properties[key] is None:
                match=re.search(pattern,line)
                if match:
                    thermo_properties[key]=float(match.group(1))
        if all(value is not None for value in thermo_properties.values()):
            break
    return thermo_properties




# combine all parsing now: SCF + OPT + FREQ
def parse_orca_output(output_text):
    scf_data=parse_scf_properties(output_text)
    opt_data=parse_optimization_properties(output_text)
    freq_data=parse_frequency_properties(output_text)
    thermo_data=parse_thermochemistry_properties(output_text)
    return{**scf_data,**opt_data,**freq_data,**thermo_data}
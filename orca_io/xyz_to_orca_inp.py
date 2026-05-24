from pathlib import Path
from orca_io.xyz_parser import read_xyz
from orca_jobs.orca_job_settings import build_orca_keywords, build_orca_optional_blocks


def xyz_to_orca_inp(xyz_file,orca_inp_folder,job,charge,multiplicity,job_profile_name,TOTAL_MEMORY_ALLOCATION_MB):
    """ 
    Generates ORCA input file name with full settings format
    """
    xyz_file=Path(xyz_file)
    orca_inp_folder=Path(orca_inp_folder)
    orca_inp_folder.mkdir(parents=True, exist_ok=True)

    keywords=build_orca_keywords(job)   #orca keyword
    optional_blocks=build_orca_optional_blocks(job,TOTAL_MEMORY_ALLOCATION_MB) #the optional block

    xyz_data=read_xyz(xyz_file)
    atoms = xyz_data["atoms"]

    # Write input file
    full_input=orca_inp_folder / f"{job_profile_name}.inp"

    with open(full_input,"w") as f:
        f.write(f"! {keywords}\n\n")
        if optional_blocks:
            f.write(optional_blocks)
            f.write("\n\n")

        f.write(f"* xyz {charge} {multiplicity}\n")

        for atom_coord in atoms:
            atom=atom_coord.atom
            f.write(
                f"{atom.symbol:2s} "
                f"{atom_coord.x:14.8f} "
                f"{atom_coord.y:14.8f} "
                f"{atom_coord.z:14.8f} \n"
            )
        f.write("*\n")
    return full_input

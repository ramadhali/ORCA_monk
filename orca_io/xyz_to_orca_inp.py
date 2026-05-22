from pathlib import Path
from orca_io.xyz_parser import read_xyz
from orca_jobs.orca_job_settings import build_orca_keywords, build_orca_optional_blocks


def xyz_to_orca_inp(xyz_file,output_folder,job,charge,multiplicity):
    xyz_file=Path(xyz_file)
    output_folder=Path(output_folder)
    output_folder.mkdir(exist_ok=True)


    keywords=build_orca_keywords(job)   #orca keyword
    optional_blocks=build_orca_optional_blocks(job) #the optional block
    label=job.label

    xyz_data=read_xyz(xyz_file)
    atoms = xyz_data["atoms"]

    out_file=output_folder/f"{xyz_file.stem}_{label}_q{charge}_m{multiplicity}.inp"   # .stem makes to take input file without extention (.xyz)
    with open(out_file,"w") as f:
        f.write(f"! {keywords}\n\n")
        if optional_blocks:
            f.write(optional_blocks)
            f.write("\n\n")

        f.write(f"* xyz {charge} {multiplicity}\n")

        for atom_coord in atoms:
            atom=atom_coord.atom
            f.write(
                f"{atom.symbol:2s} "
                f"{atom_coord.x} "
                f"{atom_coord.y} "
                f"{atom_coord.z} \n"
            )
        f.write("*\n")
    return out_file

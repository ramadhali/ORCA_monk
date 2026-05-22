from pathlib import Path
from orca_jobs.orca_job_settings import build_orca_keywords, build_orca_optional_blocks


def xyz_to_orca_inp(xyz_file,output_folder,job,charge,multiplicity):
    xyz_file=Path(xyz_file)
    output_folder=Path(output_folder)
    output_folder.mkdir(exist_ok=True)


    keywords=build_orca_keywords(job)   #orca keyword
    optional_blocks=build_orca_optional_blocks(job) #the optional block
    label=job.label

    lines=xyz_file.read_text().splitlines()
    natoms=int(lines[0])
    atom_lines=lines[2:2+natoms]

    out_file=output_folder/f"{xyz_file.stem}_{label}_q{charge}_m{multiplicity}.inp"   # .stem makes to take input file without extention (.xyz)
    with open(out_file,"w") as f:
        f.write(f"! {keywords}\n\n")
        if optional_blocks:
            f.write(optional_blocks)
            f.write("\n\n")

        f.write(f"* xyz {charge} {multiplicity}\n")

        for line in atom_lines:
            parts=line.split()
            element=parts[0]
            x,y,z=parts[1],parts[2],parts[3]
            f.write(f"{element:2s} {x} {y} {z}\n")
        f.write("*\n")
    return out_file

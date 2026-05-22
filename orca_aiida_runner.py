from pathlib import Path
from aiida_shell import launch_shell_job
from aiida.orm import SinglefileData, Dict
from orca_jobs.orca_job_settings import OrcaJob, build_orca_keywords

from orca_parsers.orca_parser_gs import parse_orca_output
import time

ws_header=[
    "molecule",
    "label",
    "functional",
    "basis",
    "solvent",
    "solvent_model",
    "grid",
    "extra_keywords",
    "tddft",
    "nroots",
    "iroot",
    "nprocs",
    "maxcore",
    "orca_keywords",
    "charge",
    "multiplicity",
    "final_energy_hartree",
    "normal_termination",
    "optimization_converged",
    "optimization_cycles",
    "n_frequencies",
    "n_imaginary_frequencies",
    "lowest_frequency_cm-1",
    "HOMO_eV",
    "LUMO_eV",
    "gap_eV",
    "zero_point_energy_hartree",
    "enthalpy_hartree",
    "gibbs_free_energy_hartree",
    "calculation_pk",
    "runtime_seconds",
]

def run_orca(
        input_filename,
        molecule,
        job: OrcaJob,
        charge,
        multiplicity,
        debug_folder,
        orca_executable
    ):
    input_file=SinglefileData(file=Path(input_filename).resolve())

    #start time stamp
    start_time=time.time()

    result,node=launch_shell_job(
        "bash",
        arguments=["-c",f"{orca_executable} orca.inp > orca.out"],
        nodes={"orca_inp":input_file},
        filenames={"orca_inp":"orca.inp"},
        outputs=["orca.out"]
    )

    # end time
    runtime_seconds=time.time()-start_time

    label = job.label
    orca_out_text=result["orca_out"].get_content()

    # save orca output file for debugging in folder

    debug_folder=Path(debug_folder)
    debug_folder.mkdir(exist_ok=True)
    orca_debug_out=debug_folder/(f"{molecule}_{label}_q{charge}_m{multiplicity}.out")
    with open(orca_debug_out,"w") as f:
        f.write(orca_out_text)

    # parring NOW!

    parsed_output=parse_orca_output(orca_out_text)

    parsed_output["molecule"] = molecule
    parsed_output["label"] = job.label
    parsed_output["functional"] = job.functional
    parsed_output["basis"] = job.basis
    parsed_output["solvent"] = job.solvent
    parsed_output["solvent_model"] = job.solvent_model
    parsed_output["grid"] = job.grid
    parsed_output["extra_keywords"] = job.extra_keywords
    parsed_output["tddft"] = job.tddft
    parsed_output["nroots"] = job.nroots
    parsed_output["iroot"] = job.iroot
    parsed_output["nprocs"] = job.nprocs
    parsed_output["maxcore"] = job.maxcore
    parsed_output["orca_keywords"] = build_orca_keywords(job)
    parsed_output["charge"] = charge
    parsed_output["multiplicity"] = multiplicity
    parsed_output["calculation_pk"] = node.pk
    parsed_output["runtime_seconds"] = runtime_seconds

    #store in Dict for aiida
    properties=Dict(dict=parsed_output).store()


    print("Calculation pk",node.pk)
    print("properties pk",properties.pk)
    print(
        f"{molecule} | {job.label} | "
        f"{parsed_output['orca_keywords']} | "
        f"q={charge} m={multiplicity} | "
        f"energy={parsed_output['final_energy_hartree']} | "
        f"runtime={runtime_seconds:.2f}s"
    )   
    return node,properties



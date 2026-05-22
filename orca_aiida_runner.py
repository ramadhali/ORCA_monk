from pathlib import Path
from aiida_shell import launch_shell_job
from aiida.orm import SinglefileData, Dict
from orca_jobs.orca_job_settings import OrcaJob, build_orca_keywords

from orca_parsers.orca_parser_gs import parse_orca_output
import time

ORCA_DATASET_FIELDS = [
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
        job: OrcaJob,   # SP/OPT/FREQ
        charge,
        multiplicity,
        debug_folder,
        orca_executable,
        verbose=True,
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

    # parsing NOW!

    orca_parsed_output=parse_orca_output(orca_out_text)

    # create dataset_row
    dataset_row = build_orca_dataset_row(
        orca_parsed_output,
        molecule,
        job,
        charge,
        multiplicity,
        node,
        runtime_seconds,
    )

    #store in Dict for aiida
    properties=Dict(dict=dataset_row).store()

    if verbose:
        print("Calculation pk",node.pk)
        print("properties pk",properties.pk)
        print(
            f"{molecule} | {job.label} | "
            f"{dataset_row['orca_keywords']} | "
            f"q={charge} m={multiplicity} | "
            f"energy={dataset_row['final_energy_hartree']} | "
            f"runtime={runtime_seconds:.2f}s"
        )   
    return node,properties


# to create dataset_row for both orca_parsed_output and workbook
def build_orca_dataset_row(
        orca_parsed_output,
        molecule,
        job: OrcaJob,
        charge,
        multiplicity,
        node,
        runtime_seconds,
):
    row = dict(orca_parsed_output)
    row["molecule"] = molecule
    row["label"] = job.label
    row["functional"] = job.functional
    row["basis"] = job.basis
    row["solvent"] = job.solvent
    row["solvent_model"] = job.solvent_model
    row["grid"] = job.grid
    row["extra_keywords"] = job.extra_keywords
    row["tddft"] = job.tddft
    row["nroots"] = job.nroots
    row["iroot"] = job.iroot
    row["nprocs"] = job.nprocs
    row["maxcore"] = job.maxcore
    row["orca_keywords"] = build_orca_keywords(job)
    row["charge"] = charge
    row["multiplicity"] = multiplicity
    row["calculation_pk"] = node.pk
    row["runtime_seconds"] = runtime_seconds

    return row
